import React from 'react';
import {CircularProgress, Container, Grid} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import ThumbUpAltIcon from "@material-ui/icons/ThumbUpAlt";
import ThumbDownAltIcon from "@material-ui/icons/ThumbDownAlt";
import {createReactionOperations} from "./Utility";

function VideoGallery({video_ids}) {
    return (
        <Grid container spacing={3}>
            {
                video_ids.map(video_id => {
                    return (<Grid item lg={4} md={6} sm={12} xs={12}>
                        <video controls width={"100%"}>
                            <source src={`/api/video/${video_id}`}
                                    type={"video/mp4"}/>
                            {"Sorry, your browser doesn't support embedded videos."}
                        </video>
                    </Grid>);
                })
            }
        </Grid>
    )
}

export default function VideoList() {
    const {id} = useParams();
    const [cacheBurst, setCacheBurst] = React.useState(1);


    const {isLoading, error, data} = useQuery(
        `/api/videolist/${id}-${cacheBurst}`,
        () => fetch(
            `/api/videolist/${id}`
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
                {
                    "An error has occurred: " + JSON.stringify(error)
                }
            </Typography>
        );
    }


    const reactionOperations = createReactionOperations(
        data["positive_reaction"],
        `/api/videolist/${id}/reaction`,
        () => setCacheBurst(cacheBurst + 1)
    )

    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                {data.title || "Loading..."}
            </Typography>
            <Typography variant={"h6"} gutterBottom>
                {data.description || "Loading..."}
            </Typography>

            <VideoGallery video_ids={(data.videos || [])}/>

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