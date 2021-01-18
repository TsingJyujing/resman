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

function Gallery({image_ids}) {
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
    return (
        <Container>
            <Grid container spacing={3}>
                {
                    image_ids.slice((pageId - 1) * pageSize, pageId * pageSize).map(image_id => {
                        const [height, setHeight] = React.useState(300);
                        const onContentVisible = () => {
                            setHeight("auto");
                        };
                        return (
                            <Grid item spacing={3} lg={4} md={6} sm={12} xs={12}>
                                <LazyLoad height={height}
                                          offsetVertical={300}
                                          onContentVisible={onContentVisible}
                                          key={image_id}>
                                    <img src={`/api/image/${image_id}`} alt={image_id} loading={"lazy"} width={"100%"}/>
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
    )
}

export default function ImageList() {
    const {id} = useParams();
    const [contextData, setContextData] = React.useState({});
    const {isLoading, error, data} = useQuery(
        `/api/imagelist/${id}`,
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
            <Gallery image_ids={(contextData.images || [])}/>

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