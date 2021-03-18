import React from "react";
import SearchIcon from "@material-ui/icons/Search";
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import SupervisorAccountIcon from '@material-ui/icons/SupervisorAccount';
import VideoLibraryIcon from '@material-ui/icons/VideoLibrary';
import ImageSearchIcon from '@material-ui/icons/ImageSearch';
import FindInPageIcon from '@material-ui/icons/FindInPage';
export const searchEntries = [
    {
        title: "Images",
        date: "",
        description: "Image threads scraped from internet",
        url: "/imagelist/",
        icon: (<ImageSearchIcon/>),
    },
    {
        title: "Videos",
        date: "",
        description: "Videos scraped from internet",
        url: "/videolist/",
        icon: (<VideoLibraryIcon/>),
    },
    {
        title: "Novels",
        date: "",
        description: "Novels scraped from internet",
        url: "/novel/",
        icon: (<FindInPageIcon/>),
    },
];


export const utilitiesEntries = [
    {
        title: "Upload Video",
        date: "",
        description: "Upload Video Manually",
        url: "/upload-video/",
        icon: (<CloudUploadIcon/>),
    },
    {
        title: "Upload Image",
        date: "",
        description: "Upload Images Manually",
        url: "/upload-image/",
        icon: (<CloudUploadIcon/>),
    },
    {
        title: "Admin Tool",
        date: "",
        description: "Admin tool for staff",
        url: "/admin/",
        icon: (<SupervisorAccountIcon/>),
    },
];
