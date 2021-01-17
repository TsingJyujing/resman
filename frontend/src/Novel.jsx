import React from 'react';
import {Button, CircularProgress, Container, Grid, MenuItem, Select} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";
import {createGetRequestUrl} from "./Utility";


import NavigateBeforeIcon from '@material-ui/icons/NavigateBefore';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';

function NovelPage({novelId}) {
    const pageSize = 4000;
    const [pageId, setPageId] = React.useState(1);

    const handleChangePageId = (event) => {
        setPageId(event.target.value);
    };


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

    const handlePreviousPage = () => {
        if (pageId > 1) {
            setPageId(pageId - 1)
        }
    };
    const handleNextPage = () => {
        if (pageId < data["page_count"]) {
            setPageId(pageId + 1);
        }
    }

    return (
        <Grid container spacing={3}>
            <Grid item spacing={3} xs={12}>
                <Typography gutterBottom variant={"body1"}>{
                    data["text"].split("\n").flatMap(text => {
                        return [text, <br/>]
                    })
                }</Typography>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Button variant="contained" color="default" fullWidth
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
                        [...Array(data["page_count"]).keys()].map(
                            i => (<MenuItem value={i + 1}>{i + 1}</MenuItem>)
                        )
                    }
                </Select>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Button variant="contained" color="primary" fullWidth
                        onClick={handleNextPage}>
                    <NavigateNextIcon/>
                </Button>
            </Grid>
        </Grid>

    );
}

export default function Novel() {
    const {id} = useParams();
    const [contextData, setContextData] = React.useState({});

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
            <NovelPage novelId={id}/>
        </Container>
    );
}