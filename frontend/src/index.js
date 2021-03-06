import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import {ThemeProvider} from '@material-ui/core/styles';
import Search from "./Search";
import ImageList from "./ImageList";
import BasicBarContainer from "./AppBasic";
import theme from './theme';
import {BrowserRouter as Router, Route, Switch, useLocation} from "react-router-dom";
import {Container, Grid, Typography} from "@material-ui/core";
import ResultItem from "./ResultItem";
import {QueryClient, QueryClientProvider} from "react-query";
import Novel from "./Novel";
import VideoList from "./VideoList";
import {searchEntries, utilitiesEntries} from "./Config";
import UploadVideo from "./UploadVideo";
import UploadImage from "./UploadImage";

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
    return (
        <Container><br/><br/>
            <Typography component={"h4"} variant={"h4"}>Search</Typography>
            <Grid container spacing={3}>
                {searchEntries.map(entry => (
                    <ResultItem post={entry}/>
                ))}
            </Grid>
            <br/><br/>
            <Typography component={"h4"} variant={"h4"}>Utilities</Typography>
            <Grid container spacing={3}>
                {utilitiesEntries.map(entry => (
                    <ResultItem post={entry}/>
                ))}
            </Grid>
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
                        <Route exact path={"/"}><Home/></Route>
                        <Route exact path={"/upload-video"}><UploadVideo/></Route>
                        <Route exact path={"/upload-image"}><UploadImage/></Route>
                        <Route exact path={"/imagelist"}><Search name={"Images"} searchRange={"imagelist"}/></Route>
                        <Route exact path={"/videolist"}><Search name={"Videos"} searchRange={"videolist"}/></Route>
                        <Route exact path={"/novel"}><Search name={"Novels"} searchRange={"novel"}/></Route>
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
