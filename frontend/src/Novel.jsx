import React from 'react';
import {Button, CircularProgress, Container, Grid, MenuItem, Select} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import {createGetRequestUrl, createReactionOperations} from "./Utility";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import NavigateNextIcon from "@material-ui/icons/NavigateNext";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import ThumbUpAltIcon from "@material-ui/icons/ThumbUpAlt";
import ThumbDownAltIcon from "@material-ui/icons/ThumbDownAlt";

function NovelPage({novelId}) {
    const pageSize = 4000;
    const [pageId, setPageId] = React.useState(1);

    const handleChangePageId = (event) => {
        setPageId(event.target.value);
    };
    const handlePreviousPage = () => {
        if (pageId > 1) {
            setPageId(pageId - 1)
        }
    };
    const handleNextPage = () => {
        if (pageId < pageCount) {
            setPageId(pageId + 1);
        }
    }

    const {isLoading, error, data} = useQuery(
        `novel-page-${novelId}-${pageId}-${pageSize}`,
        () => fetch(
            createGetRequestUrl(
                window.location,
                `/api/novel/${novelId}/data`,
                {
                    "n": pageSize, "p": pageId
                }
            )
        ).then(
            (res) => res.json()
        ), {
            cacheTime: 1000 * 60 * 20
        }
    );
    if (isLoading) {
        return <CircularProgress/>;
    }
    if (error) {
        return (<Typography>
            {
                "An error has occurred: " + JSON.stringify(error)
            }
        </Typography>);
    }

    const pageCount = data["page_count"];

    return (
        <Grid container spacing={3}>
            <Grid item spacing={3} xs={12}>
                <Typography gutterBottom variant={"body2"}>{
                    data["text"].split("\n").flatMap(text => {
                        return [text, <br/>]
                    })
                }</Typography>
            </Grid>

            <Grid item spacing={3} xs={4}>
                <Button variant="contained" color={pageId <= 1 ? "default" : "primary"} fullWidth
                        onClick={handlePreviousPage}>
                    <NavigateBeforeIcon/>
                </Button>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Select
                    id="select-page-id"
                    value={pageId}
                    onChange={handleChangePageId}
                    fullWidth
                >
                    {
                        [...Array(pageCount).keys()].map(
                            i => (<MenuItem value={i + 1}>{i + 1}</MenuItem>)
                        )
                    }
                </Select>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Button variant="contained" color={pageId >= pageCount ? "default" : "primary"} fullWidth
                        onClick={handleNextPage}>
                    <NavigateNextIcon/>
                </Button>
            </Grid>
        </Grid>
    );
}

export default function Novel() {
    const {id} = useParams();
    const [cacheBurst, setCacheBurst] = React.useState(1);

    const {isLoading, error, data} = useQuery(
        `/api/novel/${id}`,
        () => fetch(
            `/api/novel/${id}`
        ).then(
            (res) => res.json()
        ), {
            cacheTime: 1000 * 60 * 20
        }
    );
    if (isLoading) {
        return <CircularProgress/>;
    }
    if (error) {
        return (
            <Typography>
                {"An error has occurred: " + JSON.stringify(error)}
            </Typography>
        );
    }

    const reactionOperations = createReactionOperations(
        data["positive_reaction"],
        `/api/novel/${id}/reaction`,
        () => setCacheBurst(cacheBurst + 1)
    )

    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                {data.title || "Loading..."}
            </Typography>
            <NovelPage novelId={id}/>
            <Grid container>
                <Grid item xs={12}>
                    <BottomNavigation showLabels>
                        <BottomNavigationAction
                            label={data.like_count}
                            icon={<ThumbUpAltIcon color={
                                data["positive_reaction"] === true ? "primary" : "disabled"
                            }/>}
                            onClick={reactionOperations.clickLike}
                        />
                        <BottomNavigationAction
                            label={data.dislike_count}
                            icon={<ThumbDownAltIcon color={
                                data["positive_reaction"] === false ? "primary" : "disabled"
                            }/>}
                            onClick={reactionOperations.clickDislike}
                        />
                    </BottomNavigation>
                </Grid>
            </Grid>
        </Container>
    );
}