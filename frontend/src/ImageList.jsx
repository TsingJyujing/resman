import React from 'react';
import LazyLoad from 'react-lazy-load';
import {Button, CircularProgress, Container, Grid, MenuItem, Select} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import NavigateNextIcon from "@material-ui/icons/NavigateNext";

import ThumbUpAltIcon from '@material-ui/icons/ThumbUpAlt';
import ThumbDownAltIcon from '@material-ui/icons/ThumbDownAlt';
import {createReactionOperations, deleteContent} from "./Utility";
import DeleteIcon from "@material-ui/icons/Delete";

function GalleryWithoutPaginator({image_ids}) {
    return (
        <Container>
            <Grid container spacing={1}>
                {
                    image_ids.map(image_id => {
                        const [height, setHeight] = React.useState(300);
                        const onContentVisible = () => setHeight("auto");
                        return (
                            <Grid item spacing={1} lg={4} md={6} sm={12} xs={12}>
                                <LazyLoad height={height}
                                          offsetVertical={300}
                                          onContentVisible={onContentVisible}
                                          key={image_id}>
                                    <img src={`/api/image/${image_id}`} alt={image_id} loading={"lazy"}
                                         width={"100%"}/>
                                </LazyLoad>
                            </Grid>
                        )
                    })
                }
            </Grid>
        </Container>
    );
}

/**
 * Deprecated
 * @param image_ids
 * @returns {JSX.Element}
 * @constructor
 */
function GalleryWithPaginator({image_ids}) {
    const pageSize = 24;
    const [pageId, setPageId] = React.useState(1);
    const pageCount = Math.ceil(image_ids.length / pageSize)

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

    const slicedImages = image_ids.slice((pageId - 1) * pageSize, pageId * pageSize);

    return (
        <Container>
            <Grid container spacing={1}>
                {
                    slicedImages.map(image_id => {
                        const [height, setHeight] = React.useState(300);
                        const onContentVisible = () => setHeight("auto");
                        return (
                            <Grid item spacing={3} lg={4} md={6} sm={12} xs={12}>
                                <LazyLoad height={height}
                                          offsetVertical={300}
                                          onContentVisible={onContentVisible}
                                          key={image_id}>
                                    <img src={`/api/image/${image_id}`} alt={image_id} loading={"lazy"}
                                         width={"100%"}/>
                                </LazyLoad>
                            </Grid>
                        )
                    })
                }
            </Grid>

            <Grid container spacing={3}>
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
        </Container>
    );


}

const Gallery = GalleryWithoutPaginator;

export default function ImageList() {
    const {id} = useParams();
    const [cacheBurst, setCacheBurst] = React.useState(1);

    const {isLoading, error, data} = useQuery(
        `/api/imagelist/${id}-${cacheBurst}`,
        () => fetch(
            `/api/imagelist/${id}`
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
        `/api/imagelist/${id}/reaction`,
        () => setCacheBurst(cacheBurst + 1)
    )
    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                {data.title || "Loading..."}
            </Typography>
            <Typography variant={"h6"} gutterBottom>
                {data.description}
            </Typography>

            <Gallery image_ids={data.images}/>

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
                            onClick={()=>deleteContent(`/api/imagelist/${id}`)}
                        />
                    </BottomNavigation>
                </Grid>
            </Grid>
        </Container>
    );
}