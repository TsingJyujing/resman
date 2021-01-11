import React from 'react';
import LazyLoad from 'react-lazy-load';
import {Container, Grid} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {useParams} from 'react-router-dom';
import {useQuery} from "react-query";

function Gallery({image_ids}) {
    return (
        <Grid container spacing={3}>
            {
                image_ids.map(image_id => {
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
    )
}

export default function ImageThread() {
    const {id} = useParams();
    const [contextData, setContextData] = React.useState({});
    const {isLoading, error, data} = useQuery(
        `/api/image_thread/${id}`,
        () => fetch(
            `/api/image_thread/${id}`
        ).then(
            (res) => res.json()
        ), {
            cacheTime: 1000 * 60 * 20
        }
    );
    if (isLoading) return "Loading...";
    if (error) return "An error has occurred: " + JSON.stringify(error);
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
        </Container>
    );
}