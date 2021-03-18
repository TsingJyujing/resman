import React from 'react';
import {Button, Checkbox, Container, FormControlLabel, TextField, Typography} from "@material-ui/core";
import {DropzoneArea} from "material-ui-dropzone";
import {postData, postForm} from "./Utility";
import {useHistory} from "react-router";


export default function UploadImage() {
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

    const [files, setFiles] = React.useState([]);

    if (files.length > 0 && title === "") {
        setTitle(files[0].name);
    }

    const uploadFiles = () => {
        const formData = new FormData();
        formData.append("title", title);
        formData.append("description", description);
        files.forEach((file, i) => {
            formData.append(file.name, file, file.name);
        })
        const imageListDetailDataPromise = postData(
            "/api/imagelist",
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
        })
        if (like) {
            imageListDetailDataPromise.then(jsonBody => {
                const imageListId = jsonBody["id"];
                postData(`/api/imagelist/${imageListId}/reaction`, {positive_reaction: true}).then(
                    response => {
                        if (!response.ok) {
                            console.error(`Failed to set reaction on image list ${imageListId}`);
                        }
                    }
                )
            })
        }
        imageListDetailDataPromise.then(jsonBody => {
            const imageListId = jsonBody["id"];
            formData.append("image_list_id", imageListId);
            return postForm(
                "/api/image/upload",
                formData
            ).then(response => {
                if (response.ok) {
                    if (confirm("Uploaded successfully, continue uploading?")) {
                        // Refresh page
                        window.location.reload(false);
                    } else {
                        // Goto the video's page
                        history.push(`/imagelist/${imageListId}`);
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
        <TextField fullWidth required id="imagelist-title" label="Title" value={title} onChange={handleModifyTitle}/>
        <TextField multiline fullWidth id="imagelist-description" label="Description" value={description}
                   onChange={handleModifyDescription}/>
        <br/><br/>

        <DropzoneArea
            onChange={(fs) => setFiles(fs)}
            acceptedFiles={["image/*"]}
            maxFileSize={32 * 1024 * 1024}
            filesLimit={1000}
        />

        <br/><br/>
        <FormControlLabel
            control={<Checkbox checked={like} onChange={handleModifyLike} name="like"/>}
            label="Set Like to this image list"
        />
        <br/><br/>
        <Button variant="contained" color="primary" onClick={uploadFiles}>Upload</Button>
    </Container>);
}