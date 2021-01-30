import React from 'react';

import {
    BottomNavigation,
    BottomNavigationAction,
    Button,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Grid,
    Snackbar,
    TextField,
    Typography
} from "@material-ui/core";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";

import ThumbUpAltIcon from "@material-ui/icons/ThumbUpAlt";
import ThumbDownAltIcon from "@material-ui/icons/ThumbDownAlt";
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';

import {arrayEquals, createReactionOperations, deleteContent, getCookie} from "./Utility";

function Alert(props) {
    return <MuiAlert elevation={6} variant="filled" {...props} />;
}

function VideoGallery({videoIdList}) {
    return (
        <Grid container spacing={3}>
            {
                videoIdList.map(video_id => {
                    return (<Grid item lg={12} md={12} sm={12} xs={12}>
                        <video controls width={"100%"}>
                            <source src={`/api/video/${video_id}`} type={"video/mp4"}/>
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
    const [open, setOpen] = React.useState(false);
    const [modifyTitle, setModifyTitle] = React.useState(null);
    const handleModifyTitleChange = (event) => {
        setModifyTitle(event.target.value);
    }
    const [videoList, setVideoList] = React.useState([]);

    const [alertOpen, setAlertOpen] = React.useState(false)
    const handleAlertClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setAlertOpen(false);
    };


    const [modifyDescription, setModifyDescription] = React.useState(null);
    const handleModifyDescriptionChange = (event) => {
        setModifyDescription(event.target.value);
    }

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

    if (error) {
        return (
            <Typography>
                {
                    "An error has occurred: " + JSON.stringify(error)
                }
            </Typography>
        );
    }

    const stableData = isLoading ? {
        "id": id,
        "mock": true,
        "title": "",
        "description": "",
        "owner": 0,
        "positive_reaction": false,
        "like_count": 0,
        "dislike_count": 0,
        "videos": []
    } : data;

    const reactionOperations = createReactionOperations(
        stableData["positive_reaction"],
        `/api/videolist/${id}/reaction`,
        () => setCacheBurst(cacheBurst + 1)
    )

    if (!isLoading) {
        if (modifyTitle === null) {
            setModifyTitle(data.title);
        }
        if (modifyDescription === null) {
            setModifyDescription(data.description);
        }
        if (!arrayEquals(videoList, data.videos)) {
            setVideoList(data.videos);
        }
    }

    const modifyData = () => {
        fetch(
            `/api/videolist/${id}`,
            {
                method: 'PATCH',
                body: JSON.stringify({
                    "title": modifyTitle,
                    "description": modifyDescription
                }),
                cache: 'no-cache',
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Accept": "application/json",
                    'Content-Type': 'application/json'
                },
                redirect: 'follow', // manual, *follow, error
            }
        ).then(response => {
            if (response.ok) {
                setAlertOpen(true);
            } else {
                alert("Failed while modifying the information.")
            }
            setCacheBurst(cacheBurst + 1);

        })
        setOpen(false)
    }

    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                {stableData.title || "No title"}
            </Typography>
            <Typography variant={"h6"} gutterBottom>
                {stableData.description || "No description"}
            </Typography>

            <VideoGallery videoIdList={videoList}/>

            <br/><br/>

            <Grid container>
                <Grid item xs={12}>
                    <BottomNavigation showLabels>
                        <BottomNavigationAction
                            label={"Edit"}
                            icon={<EditIcon color={"primary"}/>}
                            onClick={() => setOpen(true)}
                        />
                        <BottomNavigationAction
                            label={stableData.like_count}
                            icon={<ThumbUpAltIcon color={
                                stableData["positive_reaction"] === true ? "primary" : "disabled"
                            }/>}
                            onClick={reactionOperations.clickLike}
                        />
                        <BottomNavigationAction
                            label={stableData.dislike_count}
                            icon={<ThumbDownAltIcon color={
                                stableData["positive_reaction"] === false ? "primary" : "disabled"
                            }/>}
                            onClick={reactionOperations.clickDislike}
                        />
                        <BottomNavigationAction
                            label={"Delete"}
                            icon={<DeleteIcon color={"error"}/>}
                            onClick={() => deleteContent(`/api/videolist/${id}`)}
                        />
                    </BottomNavigation>
                </Grid>

                <Dialog open={open} onClose={() => setOpen(false)} aria-labelledby="form-dialog-title">
                    <DialogTitle id="form-dialog-title">Modify</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Please modify these information
                        </DialogContentText>
                        <TextField
                            autoFocus
                            margin="dense"
                            id="title"
                            label="Title"
                            fullWidth
                            value={modifyTitle}
                            onChange={handleModifyTitleChange}
                        />
                        <TextField
                            margin="dense"
                            id="description"
                            label="Description"
                            value={modifyDescription}
                            onChange={handleModifyDescriptionChange}
                            fullWidth
                            multiline
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={modifyData} color="primary">
                            Modify
                        </Button>
                        <Button onClick={() => setOpen(false)} color="primary">
                            Cancel
                        </Button>
                    </DialogActions>
                </Dialog>
                <Snackbar
                    open={alertOpen}
                    autoHideDuration={2000}
                    message={"Information modified successfully."}
                    onClose={handleAlertClose}
                >
                </Snackbar>
            </Grid>
        </Container>
    );
}