import React from 'react';
import ReactDOM from 'react-dom';
import { GeoJsonLayer } from 'deck.gl';

import DeckGLContainer from './DeckGLContainer';

const keyMap = {
  color: 'fillColor',
}


function DeckGeoJsonLayer(slice, payload, setControlValue) {
  const fd = slice.formData;
  console.log(payload)
  const c = fd.color_picker;
  const data = payload.data.geojson.features.map(d => {
    d.properties.fillColor =  [c.r, c.g, c.b, 255 * c.a]
    d.properties.elevation = 2000
    return d
  });

/*
  geojson.features.properties = {
    lineColor: [r,g,b,a]
    lineWidth: int
    fillColor: [r,g,b,a]
    radius: int
    elevation: int
  }
*/

  const layer = new GeoJsonLayer({
    id: `geojson-layer`,
    data,
    filled: true,
    stroked: false,
    extruded: true,
    pointRadiusScale: 100,
  });

  const viewport = {
    ...fd.viewport,
    width: slice.width(),
    height: slice.height(),
  };
  ReactDOM.render(
    <DeckGLContainer
      mapboxApiAccessToken={payload.data.mapboxApiKey}
      viewport={viewport}
      layers={[layer]}
      mapStyle={fd.mapbox_style}
      setControlValue={setControlValue}
    />,
    document.getElementById(slice.containerId),
  );
}
module.exports = DeckGeoJsonLayer;
