import React from 'react';
import {CircularProgress, Container, Grid} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import {createGetRequestUrl, createReactionOperations, deleteContent} from "./Utility";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import ThumbUpAltIcon from "@material-ui/icons/ThumbUpAlt";
import ThumbDownAltIcon from "@material-ui/icons/ThumbDownAlt";
import DeleteIcon from "@material-ui/icons/Delete";
import DescriptionBlock from "./DescriptionBlock";
import {PaginatorWithCombo} from "./components/Paginator";

function NovelPage({novelId}) {
    const pageSize = 4000;
    const [pageId, setPageId] = React.useState(1);

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
        <Container>
            <Grid container spacing={3}>
                <Grid item spacing={3} xs={12}>
                    <DescriptionBlock text={data["text"]}/>
                </Grid>
            </Grid>
            <PaginatorWithCombo pageId={pageId} setPageId={setPageId} pageCount={pageCount}/>
        </Container>
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
                {data.title || "No title"}
            </Typography>
            <NovelPage novelId={id}/>
            <br/>
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
                        <BottomNavigationAction
                            label={"Delete"}
                            icon={<DeleteIcon color={"error"}/>}
                            onClick={() => deleteContent(`/api/novel/${id}`)}
                        />
                    </BottomNavigation>
                </Grid>
            </Grid>
        </Container>
    );
}