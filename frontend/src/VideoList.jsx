import React from 'react';
import {CircularProgress, Container, Grid} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import ThumbUpAltIcon from "@material-ui/icons/ThumbUpAlt";
import ThumbDownAltIcon from "@material-ui/icons/ThumbDownAlt";

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
    const [contextData, setContextData] = React.useState({});
    const {isLoading, error, data} = useQuery(
        `/api/videolist/${id}`,
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
    if (Object.keys(contextData).length <= 0) {
        setContextData(data);
    }
    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                {contextData.title || "Loading..."}
            </Typography>
            <Typography variant={"h6"} gutterBottom>
                {contextData.description || "Loading..."}
            </Typography>

            <VideoGallery video_ids={(contextData.videos || [])}/>

            <Grid container>
                <Grid item xs={12}>
                    {/*TODO add change reaction and refresh data*/}
                    <BottomNavigation showLabels>
                        <BottomNavigationAction
                            label={contextData.like_count}
                            icon={<ThumbUpAltIcon color={
                                contextData["positive_reaction"] === true ? "primary" : "disabled"
                            }/>}
                        />
                        <BottomNavigationAction
                            label={contextData.dislike_count}
                            icon={<ThumbDownAltIcon color={
                                contextData["positive_reaction"] === false ? "primary" : "disabled"
                            }/>}
                        />
                    </BottomNavigation>
                </Grid>
            </Grid>
        </Container>
    );
}