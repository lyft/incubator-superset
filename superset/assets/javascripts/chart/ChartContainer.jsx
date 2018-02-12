import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import * as Actions from './chartAction';
import Chart from './Chart';

const testData = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [
              -122.4264907836914,
              37.78726741375342,
            ],
            [
              -122.45807647705078,
              37.790794553924414,
            ],
            [
              -122.4755859375,
              37.759858513184625,
            ],
            [
              -122.431640625,
              37.74329970164701,
            ],
            [
              -122.40623474121092,
              37.76772943539666,
            ],
            [
              -122.4264907836914,
              37.78726741375342,
            ],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [
              -122.48245239257812,
              37.68871084320727,
            ],
            [
              -122.4031448364258,
              37.68871084320727,
            ],
            [
              -122.4031448364258,
              37.72782336496339,
            ],
            [
              -122.48245239257812,
              37.72782336496339,
            ],
            [
              -122.48245239257812,
              37.68871084320727,
            ],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [
              -122.51266479492188,
              37.77532815168286,
            ],
            [
              -122.53807067871094,
              37.76637243960179,
            ],
            [
              -122.53257751464842,
              37.748457761603355,
            ],
            [
              -122.50442504882814,
              37.74302821484915,
            ],
            [
              -122.4872589111328,
              37.756872771856465,
            ],
            [
              -122.51266479492188,
              37.77532815168286,
            ],
          ],
        ],
      },
    },
  ],
};

function mapStateToProps({ charts }, ownProps) {
  const chart = charts[ownProps.chartKey];
  return {
    annotationData: chart.annotationData,
    geoAnnotationData: testData,
    chartAlert: chart.chartAlert,
    chartStatus: chart.chartStatus,
    chartUpdateEndTime: chart.chartUpdateEndTime,
    chartUpdateStartTime: chart.chartUpdateStartTime,
    latestQueryFormData: chart.latestQueryFormData,
    lastRendered: chart.lastRendered,
    queryResponse: chart.queryResponse,
    queryRequest: chart.queryRequest,
    triggerQuery: chart.triggerQuery,
  };
}

function mapDispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(Actions, dispatch),
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Chart);
