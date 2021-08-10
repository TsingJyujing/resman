import React from 'react';
import useQueryString from "../components/useQueryString";
import {CircularProgress, Container, Grid, Typography} from "@material-ui/core";
import {useQuery} from "react-query";
import {createGetRequestUrl} from "../Utility";
import ResultItem from "../components/ResultItem";
import {Paginator} from "../components/Paginator";

function ContentRecommendationResults({searchRange, page, pageSize}) {
    const {isLoading, error, data} = useQuery(
        `Recommend(${searchRange})(p=${page},n=${pageSize})`,
        () => fetch(
            createGetRequestUrl(
                window.location,
                `/api/recsys/${searchRange}`,
                {
                    "p": page,
                    "n": pageSize,
                }
            ).toString()
        ).then(
            resp => resp.json()
        ),
        {cacheTime: 1000 * 60 * 20}
    );
    if (isLoading) {
        return <CircularProgress/>;
    }
    if (error) {
        return (
            <Typography>
                {
                    "An error has occurred: " + JSON.stringify(error)
                }
            </Typography>
        );
    }
    if (data.length > 0) {
        return (
            <Grid container spacing={3}>
                {/*TODO modularization this*/}
                {
                    data.map(postElement => (
                        <ResultItem key={postElement.id} post={{
                            title: postElement.title,
                            date: postElement.updated || "-",
                            description: postElement.description || "-",
                            url: `/${searchRange}/${postElement.id}`
                        }}/>
                    ))
                }
            </Grid>
        );
    } else {
        return (
            <Typography>
                Can't find any result
            </Typography>
        );
    }

}

export default function ({name, searchRange}) {
    document.title = `Recommendation of ${name}`;
    const [pageId, setPageId] = useQueryString("p", 1);
    const pageSize = 20;

    return (
        <Container maxWidth="lg">

            <ContentRecommendationResults
                searchRange={searchRange}
                page={pageId}
                pageSize={pageSize}
            />

            <Paginator pageId={pageId} setPageId={setPageId}/>

        </Container>
    );
}