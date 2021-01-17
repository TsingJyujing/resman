import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import {ThemeProvider} from '@material-ui/core/styles';
import Search from "./Search";
import ImageList from "./ImageList";
import BasicBarContainer from "./AppBasic";
import theme from './theme';
import {BrowserRouter as Router, Route, Switch, useLocation} from "react-router-dom";
import {Container} from "@material-ui/core";
import ResultItem from "./ResultItem";
import {QueryClient, QueryClientProvider} from "react-query";
import Novel from "./Novel";
import VideoList from "./VideoList";

const queryClient = new QueryClient();

function NoMatch() {
    let location = useLocation();
    return (
        <div>
            <h3>
                Location <code>{location.pathname}</code> not found
            </h3>
            <a href={"/"}><h6>Home</h6></a>
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
        {/*<QueryClientProvider client={queryClient}>*/}
        <ThemeProvider theme={theme}>
            <CssBaseline/>
            <QueryClientProvider client={queryClient}>
                <BasicBarContainer>
                    <Switch>
                        <Route exact path={"/"}><Search/></Route>
                        <Route path="/imagelist/:id"><ImageList/></Route>
                        <Route path="/videolist/:id"><VideoList/></Route>
                        <Route path="/novel/:id"><Novel/></Route>
                        <Route path="*">
                            <NoMatch/>
                        </Route>
                    </Switch>
                </BasicBarContainer>
            </QueryClientProvider>

        </ThemeProvider>
        {/*</QueryClientProvider>*/}
    </Router>,
    document.querySelector('#root'),
);
