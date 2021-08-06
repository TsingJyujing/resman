import React from 'react';
import useQueryString from "./useQueryString";
import {CircularProgress, Container, Grid, Typography} from "@material-ui/core";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import FirstPageIcon from "@material-ui/icons/FirstPage";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import Icon from "@material-ui/core/Icon";
import NavigateNextIcon from "@material-ui/icons/NavigateNext";
import {useQuery} from "react-query";
import {createGetRequestUrl} from "./Utility";
import ResultItem from "./ResultItem";

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

    const modifyPageId = (newPageId) => {
        if (newPageId <= 1) {
            setPageId(1);
        } else {
            setPageId(newPageId);
        }
    };


    return (
        <Container maxWidth="lg">

            <ContentRecommendationResults
                searchRange={searchRange}
                page={pageId}
                pageSize={pageSize}
            />

            {/*TODO modularization this*/}
            <Grid container spacing={3}>
                <Grid item sm={12} md={12} lg={12} xs={12}>
                    <BottomNavigation>
                        <BottomNavigationAction label="First" icon={<FirstPageIcon/>} onClick={() => modifyPageId(1)}/>
                        <BottomNavigationAction label="Previous" icon={<NavigateBeforeIcon/>}
                                                onClick={() => modifyPageId(pageId - 1)}/>
                        <BottomNavigationAction label="Current" icon={<Icon>{pageId}</Icon>} onClick={() => {
                            const pageIdInput = prompt("Please input page num:", `${pageId}`);
                            if (pageIdInput != null) {
                                modifyPageId(parseInt(pageIdInput));
                            }
                        }}/>
                        <BottomNavigationAction label="Next" icon={<NavigateNextIcon/>}
                                                onClick={() => modifyPageId(pageId + 1)}/>
                    </BottomNavigation>
                </Grid>
            </Grid>

        </Container>
    );
}