import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import MockContent from './MockContent';
import Search from "./Search";
import ImageThread from "./ImageThread";
import BasicBarContainer from "./AppBasic";
import theme from './theme';

ReactDOM.render(
  <ThemeProvider theme={theme}>
    {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
    <CssBaseline />
    <BasicBarContainer>
    {/* <MockContent /> */}
    <ImageThread/>
    </BasicBarContainer>
  </ThemeProvider>,
  document.querySelector('#root'),
);
