/* eslint no-underscore-dangle: ["error", { "allow": ["", "__timestamp"] }] */

import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

import { GeoJsonLayer } from 'deck.gl';

import AnimatableDeckGLContainer from '../AnimatableDeckGLContainer';

import * as common from './common';
import { getPlaySliderParams } from '../../../modules/time';
import sandboxedEval from '../../../modules/sandbox';

function getPoints(geojson) {
  const points = [];
  Object.values(geojson).forEach((geometry) => {
    geometry.coordinates.forEach((polygon) => {
      polygon.forEach((coordinates) => {
        coordinates.forEach((point) => {
          points.push(point);
        });
      });
    });
  });
  return points;
}

function getLayer(formData, payload, slice, filters) {
  const fd = formData;
  let data = payload.data.features.map(d => ({ ...d, geometry: payload.data.geojson[d.zipcode] }));
  data = data.filter(d => d.geometry !== undefined);

  if (filters != null) {
    filters.forEach((f) => {
      data = data.filter(f);
    });
  }

  // find values range
  let minValue = Infinity;
  let maxValue = -Infinity;
  data.forEach((d) => {
    if (d.geometry !== null) {
      minValue = Math.min(minValue, d.metric);
      maxValue = Math.max(maxValue, d.metric);
    }
  });

  const c = fd.color_picker || { r: 0, g: 0, b: 0, a: 1 };
  data = data.map(d => ({
    ...d,
    properties: {
      color: [c.r, c.g, c.b, 255 * c.a * (d.metric - minValue) / (maxValue - minValue)],
      metric: d.metric,
      zipcode: d.zipcode,
    },
  }));

  if (fd.js_data_mutator) {
    // Applying user defined data mutator if defined
    const jsFnMutator = sandboxedEval(fd.js_data_mutator);
    data = jsFnMutator(data);
  }

  const layerProps = common.commonLayerProps(fd, slice);
  if (layerProps.onHover === undefined) {
    layerProps.pickable = true;
    layerProps.onHover = (o) => {
      if (o.picked) {
        slice.setTooltip({
          content: 'ZIP code: ' + o.object.zipcode + '<br />Metric: ' + o.object.metric,
          x: o.x,
          y: o.y + 75,  // weird offset
        });
      } else {
        slice.setTooltip(null);
      }
    };
  }

  return new GeoJsonLayer({
    id: `zipcodes-layer-${fd.slice_id}`,
    data,
    pickable: true,
    stroked: true,
    filled: true,
    extruded: false,
    lineWidthScale: 20,
    lineWidthMinPixels: 1,
    getFillColor: d => d.properties.color,
    getLineColor: [0, 0, 0, 100],
    getRadius: 100,
    getLineWidth: 1,
    getElevation: 30,
    ...layerProps,
  });
}

const propTypes = {
  slice: PropTypes.object.isRequired,
  payload: PropTypes.object.isRequired,
  setControlValue: PropTypes.func.isRequired,
  viewport: PropTypes.object.isRequired,
};

class DeckGLZipCodes extends React.PureComponent {
  /* eslint-disable-next-line react/sort-comp */
  static getDerivedStateFromProps(nextProps) {
    const fd = nextProps.slice.formData;
    const features = nextProps.payload.data.features || [];

    const timeGrain = fd.time_grain_sqla || fd.granularity || 'PT1M';
    const timestamps = features.map(f => f.__timestamp);
    const { start, end, step, values, disabled } = getPlaySliderParams(timestamps, timeGrain);

    return { start, end, step, values, disabled };
  }
  constructor(props) {
    super(props);
    this.state = DeckGLZipCodes.getDerivedStateFromProps(props);

    this.getLayers = this.getLayers.bind(this);
  }
  componentWillReceiveProps(nextProps) {
    this.setState(DeckGLZipCodes.getDerivedStateFromProps(nextProps, this.state));
  }
  getLayers(values) {
    if (this.props.payload.data.features === undefined) {
      return [];
    }

    const filters = [];

    // time filter
    if (values[0] === values[1] || values[1] === this.end) {
      filters.push(d => d.__timestamp >= values[0] && d.__timestamp <= values[1]);
    } else {
      filters.push(d => d.__timestamp >= values[0] && d.__timestamp < values[1]);
    }

    const layer = getLayer(
      this.props.slice.formData,
      this.props.payload,
      this.props.slice,
      filters);

    return [layer];
  }
  render() {
    return (
      <div>
        <AnimatableDeckGLContainer
          getLayers={this.getLayers}
          start={this.state.start}
          end={this.state.end}
          step={this.state.step}
          values={this.state.values}
          disabled={this.state.disabled}
          viewport={this.props.viewport}
          mapboxApiAccessToken={this.props.payload.data.mapboxApiKey}
          mapStyle={this.props.slice.formData.mapbox_style}
          setControlValue={this.props.setControlValue}
          aggregation
        />
      </div>
    );
  }
}

DeckGLZipCodes.propTypes = propTypes;

function deckZipCodes(slice, payload, setControlValue) {
  const fd = slice.formData;
  let viewport = {
    ...fd.viewport,
    width: slice.width(),
    height: slice.height(),
  };

  if (fd.autozoom && payload.data.geojson) {
    viewport = common.fitViewport(viewport, getPoints(payload.data.geojson));
  }

  ReactDOM.render(
    <DeckGLZipCodes
      slice={slice}
      payload={payload}
      setControlValue={setControlValue}
      viewport={viewport}
    />,
    document.getElementById(slice.containerId),
  );
}

module.exports = {
  default: deckZipCodes,
  getLayer,
};
