import React from 'react';
import ReactDOM from 'react-dom';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

import 'react-bootstrap-table/css/react-bootstrap-table.css';
import './tag.css';


function linkFormatter(cell, row) {
  const url = `${cell}`;
  return <a href={url} rel="noopener noreferrer" target="_blank">{row.name}</a>;
}


function onChangeFormatter(cell) {
  const date = new Date(cell);
  return date.toLocaleString();
}


function tagWidget(slice, payload) {
  slice.container.css('height', slice.height());

  const data = payload.data.map(obj => ({
      ...obj,
      link: <a href={obj.url}>{obj.name}</a>,
  }));

  ReactDOM.render(
    <BootstrapTable
      data={data}
      bordered={false}
      height={slice.height()}
      scrollTop={'Top'}
      tableHeaderClass="tag-header-class"
      tableBodyClass="tag-body-class"
      containerClass="tag-container-class"
      tableContainerClass="tag-table-container-class"
      headerContainerClass="tag-header-container-class"
      bodyContainerClass="tag-body-container-class"
    >
      <TableHeaderColumn dataField="id" isKey hidden>ID</TableHeaderColumn>
      <TableHeaderColumn
        dataField="url"
        dataFormat={linkFormatter}
      >Name</TableHeaderColumn>
      <TableHeaderColumn dataField="type" dataSort>Type</TableHeaderColumn>
      <TableHeaderColumn
        dataField="changed_on"
        dataFormat={onChangeFormatter}
        dataSort
      >Changed on</TableHeaderColumn>
    </BootstrapTable>,
    document.getElementById(slice.containerId),
  );
}


module.exports = tagWidget;
