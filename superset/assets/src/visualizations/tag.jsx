import React from 'react';
import ReactDOM from 'react-dom';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

import 'react-bootstrap-table/css/react-bootstrap-table.css';
import './tag.css';


function tagWidget(slice, payload) {
  slice.container.css('height', slice.height());
  ReactDOM.render(
    <BootstrapTable data={payload.data} striped hover>
      <TableHeaderColumn dataField="id" isKey>ID</TableHeaderColumn>
      <TableHeaderColumn dataField="type" dataSort>Type</TableHeaderColumn>
      <TableHeaderColumn dataField="url">URL</TableHeaderColumn>
    </BootstrapTable>,
    document.getElementById(slice.containerId),
  );
}


module.exports = tagWidget;
