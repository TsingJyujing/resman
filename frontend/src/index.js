import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import {ThemeProvider} from '@material-ui/core/styles';
import MockContent from './MockContent';
import Search from "./Search";
import ImageThread from "./ImageThread";
import BasicBarContainer from "./AppBasic";
import theme from './theme';
import {BrowserRouter as Router, Route, Switch, useLocation} from "react-router-dom";
import {Container} from "@material-ui/core";
import ResultItem from "./ResultItem";

function NoMatch() {
    let location = useLocation();
    return (
        <div>
            <h3>
                No match for <code>{location.pathname}</code>
            </h3>
        </div>
    );
}

function Home() {
    const entries = [
        {
            title: "Images",
            date: "",
            description: "Image threads scraped from internet",
            url: "/image"
        }
    ];
    return (
        <Container>
            <br/><br/>
            {entries.map(entry => (
                <ResultItem post={entry}/>
            ))}
        </Container>
    )
}

ReactDOM.render(
    <Router>
        <ThemeProvider theme={theme}>
            <CssBaseline/>
            <BasicBarContainer>
                <Switch>
                    <Route exact path={"/"}><Home/></Route>
                    <Route exact path="/image"><Search/></Route>
                    <Route path="/mock"><MockContent/></Route>
                    <Route path="/image/:id"><ImageThread/></Route>
                    <Route path="*">
                        <NoMatch/>
                    </Route>
                </Switch>
            </BasicBarContainer>
        </ThemeProvider>
    </Router>,
    document.querySelector('#root'),
);
