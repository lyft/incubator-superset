import React from 'react';
import ReactDOM from 'react-dom';

import { GeoJsonLayer, ScatterplotLayer } from 'deck.gl';

import DeckGLContainer from './../DeckGLContainer';

import * as common from './common';
import { getColorFromScheme, hexToRGB } from '../../../javascripts/modules/colors';
import { unitToRadius } from '../../../javascripts/modules/geo';
import sandboxedEval from '../../../javascripts/modules/sandbox';

function getLayer(formData, payload, slice) {
  const fd = formData;
  const c = fd.color_picker || { r: 0, g: 0, b: 0, a: 1 };
  const fixedColor = [c.r, c.g, c.b, 255 * c.a];

  let data = payload.data.features.map((d) => {
    let radius = unitToRadius(fd.point_unit, d.radius) || 10;
    if (fd.multiplier) {
      radius *= fd.multiplier;
    }
    let color;
    if (fd.dimension) {
      color = hexToRGB(getColorFromScheme(d.cat_color, fd.color_scheme), c.a * 255);
    } else {
      color = fixedColor;
    }
    return {
      ...d,
      radius,
      color,
    };
  });

  if (fd.js_data_mutator) {
    // Applying user defined data mutator if defined
    const jsFnMutator = sandboxedEval(fd.js_data_mutator);
    data = jsFnMutator(data);
  }

  return new ScatterplotLayer({
    id: `scatter-layer-${fd.slice_id}`,
    data,
    fp64: true,
    outline: false,
    ...common.commonLayerProps(fd, slice),
  });
}

function deckScatter(slice, payload, setControlValue) {
  const fd = slice.formData;
  const layers = [];
  console.log('HAS DATA?', slice.geoAnnotationData);
  if (slice.geoAnnotationData) {
    // TODO: move into a function that returns the layer (geoAnnotationLayer?)
    let data;
    if (slice.geoAnnotationData.type === 'FeatureCollection') {
      data = slice.geoAnnotationData.features;
    } else if (slice.geoAnnotationData.type === 'Feature') {
      data = [slice.geoAnnotationData];
    } else {
      throw new Error('Unrecognized GeoJSON type for annotation');
    }
    const geoJsonLayer = new GeoJsonLayer({
      id: 'test',
      filled: true,           // fd.filled
      data,
      stroked: true,          // fd.stroked
      extruded: false,        // fd.extruded
      pointRadiusScale: 100,  // fd.point_radius_scale
      ...common.commonLayerProps(fd, slice),
    });
    layers.push(geoJsonLayer);
  }
  layers.push(getLayer(fd, payload, slice));

  const viewport = {
    ...slice.formData.viewport,
    width: slice.width(),
    height: slice.height(),
  };

  ReactDOM.render(
    <DeckGLContainer
      mapboxApiAccessToken={payload.data.mapboxApiKey}
      viewport={viewport}
      layers={layers}
      mapStyle={slice.formData.mapbox_style}
      setControlValue={setControlValue}
    />,
    document.getElementById(slice.containerId),
  );
}

module.exports = {
  default: deckScatter,
  getLayer,
};
