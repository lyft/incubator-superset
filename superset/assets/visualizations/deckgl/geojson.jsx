import React from 'react';
import ReactDOM from 'react-dom';
import { GeoJsonLayer } from 'deck.gl';

import DeckGLContainer from './DeckGLContainer';

function DeckGeoJsonLayer(slice, payload, setControlValue) {
  console.log(payload)
  const fd = slice.formData;
  const c = fd.color_picker;
  // const data = payload.data.features.map(d => ({
  //   ...d,
  //   color: [c.r, c.g, c.b, 255 * c.a],
  // }));

  const sample_geojson_data = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Point",
        "coordinates": [
          -122.43335723876952,
          37.784282779035216
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -122.4213409423828,
              37.76895071032235
            ],
            [
              -122.39713668823241,
              37.76895071032235
            ],
            [
              -122.39713668823241,
              37.791337175930686
            ],
            [
              -122.4213409423828,
              37.791337175930686
            ],
            [
              -122.4213409423828,
              37.76895071032235
            ]
          ]
        ]
      }
    }
  ]
}

  const layer = new GeoJsonLayer({
    id: `geojson-layer`,
    data: sample_geojson_data,
    filled: true,
    stroked: false,
    extruded: true,
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
