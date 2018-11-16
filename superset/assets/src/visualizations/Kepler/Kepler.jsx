import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import KeplerGl from 'kepler.gl';
import KeplerGlSchema from 'kepler.gl/schemas';
import { addDataToMap } from 'kepler.gl/actions';
import Processors from 'kepler.gl/processors';
import shortid from 'shortid';

import './Kepler.css';


const propTypes = {
  height: PropTypes.number,
  setControlValue: PropTypes.func,
};

class Kepler extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      keplerId: shortid.generate(),
    };
    this.setMapConfig = this.setMapConfig.bind(this);
  }
  componentDidMount() {
    this.addDataToMap(this.props);
  }
  componentWillReceiveProps(nextProps) {
    if (nextProps.features !== this.props.features) {
      this.addDataToMap(nextProps, false);
      this.setMapConfig();
    }
  }
  getCurrentConfig() {
    const { keplerGl } = this.props;
    return KeplerGlSchema.getConfigToSave(keplerGl[this.state.keplerId]);
  }
  setMapConfig() {
    const { setControlValue } = this.props;
    setControlValue('config', JSON.stringify(this.getCurrentConfig(), null, 2));
  }
  addDataToMap(props, useControlConfig = true) {
    let config = props.config;
    if (!config) {
      config = null;
    } else {
      config = useControlConfig ? JSON.parse(config) : this.getCurrentConfig();
    }
    const data = Processors.processRowObject(props.features);
    const datasets = [{
      data,
      info: {
        id: 'main',
        label: 'data',
      },
    }];
    props.dispatch(addDataToMap({ datasets, config }));
  }
  render() {
    return (
      <div>
        <KeplerGl
          id={this.state.keplerId}
          onSaveMap={this.setMapConfig}
          {...this.props}
        />
      </div>);
  }
}

Kepler.displayName = 'Kepler';
Kepler.propTypes = propTypes;

const mapStateToProps = state => ({ keplerGl: state.keplerGl });
const dispatchToProps = dispatch => ({ dispatch });
export default connect(mapStateToProps, dispatchToProps)(Kepler);
