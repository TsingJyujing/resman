import React from 'react';
import {
    Box,
    Button, Checkbox,
    Container,
    FormControlLabel,
    List,
    ListItem,
    ListItemText,
    Paper,
    TextField,
    Typography
} from "@material-ui/core";
// import {DropzoneArea} from "material-ui-dropzone";
import {formatBytes, postData, postForm} from "./Utility";
import {useHistory} from "react-router";
import {useDropzone} from "react-dropzone";

export default function UploadVideo() {
    const history = useHistory();
    const [title, setTitle] = React.useState("");
    const handleModifyTitle = (event) => {
        setTitle(event.target.value);
    };

    const [description, setDescription] = React.useState("");
    const handleModifyDescription = (event) => {
        setDescription(event.target.value);
    };
 const [like, setLike] = React.useState(false);
    const handleModifyLike = (event) => {
        setLike(event.target.checked);
    };


    const {acceptedFiles: files, getRootProps, getInputProps} = useDropzone({
        accept: ["video/mp4"]
    });

    if (files.length > 0 && title === "") {
        setTitle(files[0].name);
    }

    const uploadFiles = () => {
        const formData = new FormData();
        formData.append("title", title);
        formData.append("description", description);
        files.forEach((file, i) => {
            formData.append(`video_${i}.mp4`, file, `video_${i}.mp4`);
        })
        const videoListDetailDataPromise = postData(
            "/api/videolist",
            {
                "title": title,
                "description": description
            }
        ).then(response => {
            if (response.ok) {
                return response.json()
            } else {
                console.log(response);
                throw Error("Error while creating list.")
            }
        });

        if (like) {
            videoListDetailDataPromise.then(jsonBody => {
                const videoListId = jsonBody["id"];
                postData(`/api/videolist/${videoListId}/reaction`, {positive_reaction: true}).then(
                    response => {
                        if (!response.ok) {
                            console.error(`Failed to set reaction on video list ${videoListId}`);
                        }
                    }
                )
            })
        }

        videoListDetailDataPromise.then(jsonBody => {
            const videoListId = jsonBody["id"];
            formData.append("video_list_id", videoListId);
            return postForm(
                "/api/video/upload",
                formData
            ).then(response => {
                if (response.ok) {
                    if (confirm("Uploaded successfully, continue uploading?")) {
                        // Refresh page
                        window.location.reload(false);
                    } else {
                        // Goto the video's page
                        history.push(`/videolist/${videoListId}`);
                    }
                } else {
                    console.error("Error while uploading file, got response:")
                    console.error(response);
                    alert("Upload failed.")
                }
            })
        })
    }

    return (<Container maxWidth={"md"}>
        <br/>
        <Typography component={"h4"} variant={"h4"}> Upload Images</Typography>
        <TextField fullWidth required id="video-title" label="Title" value={title} onChange={handleModifyTitle}/>
        <TextField multiline fullWidth id="video-description" label="Description" value={description}
                   onChange={handleModifyDescription}/>
        <br/><br/>

        {/*TODO use this after bug fixed: https://github.com/Yuvaleros/material-ui-dropzone/issues/268*/}
        {/*<DropzoneArea*/}
        {/*    onChange={(fs) => setFiles(fs)}*/}
        {/*    acceptedFiles={["video/mp4"]}*/}
        {/*    maxFileSize={5000000000}*/}
        {/*/>*/}

        <Container maxWidth="lg">
            <Paper>
                <Box {...getRootProps({className: 'dropzone'})}>
                    <input {...getInputProps()} />
                    <Typography component={"h5"} variant={"h5"}>Drag 'n' drop some files here, or click to select files</Typography>
                </Box>
                <List dense={false}>
                    {files.map(file => (
                        <ListItem>
                            <ListItemText
                                primary={file.name}
                                secondary={`Size: ${formatBytes(file.size)}`}
                            />
                        </ListItem>
                    ))}
                </List>
            </Paper>
        </Container>
        <br/><br/>
          <FormControlLabel
            control={<Checkbox checked={like} onChange={handleModifyLike} name="like"/>}
            label="Set Like to this video list"
        />
        <br/><br/>
        <Button variant="contained" color="primary" onClick={uploadFiles}>Upload</Button>
    </Container>);
}