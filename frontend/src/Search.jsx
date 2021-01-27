import React from 'react';

import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import SearchIcon from "@material-ui/icons/Search";

import {makeStyles} from '@material-ui/core/styles';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Button,
    CircularProgress,
    Container,
    FormControl,
    Grid,
    InputAdornment,
    InputLabel,
    MenuItem,
    Select,
    TextField,
    Typography
} from '@material-ui/core';
import {useQuery} from "react-query";

import ResultItem from "./ResultItem";
import theme from "./theme";
import {createGetRequestUrl} from "./Utility";

import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';

import FirstPageIcon from '@material-ui/icons/FirstPage';
import NavigateBeforeIcon from '@material-ui/icons/NavigateBefore';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';

import ImageIcon from '@material-ui/icons/Image';
import VideoLibraryIcon from '@material-ui/icons/VideoLibrary';
import MenuBookIcon from '@material-ui/icons/MenuBook';

import Icon from "@material-ui/core/Icon";

const useStyles = makeStyles((theme) => ({
    heading: {
        fontSize: theme.typography.pxToRem(15),
        fontWeight: theme.typography.fontWeightRegular,
    },
    searchButton: {
        height: "57px"
    },
    rangeSelect: {
        height: "39px"
    }
}));


function ContentSearchResults({searchRange, query, page, pageSize, searchAccuracy, similarWords}) {

    const queryCondition = query === "" ? {
        "p": page,
        "n": pageSize,
        "sw": similarWords
    } : {
        "q": query,
        "p": page,
        "n": pageSize,
        "a": searchAccuracy,
        "sw": similarWords
    };
    const {isLoading, error, data} = useQuery(
        `Query(${searchRange})(${JSON.stringify(queryCondition)})`,
        () => fetch(
            createGetRequestUrl(
                window.location,
                `/api/${searchRange}`,
                queryCondition
            ).toString()
        ).then(
            resp => resp.json()
        ),
        {cacheTime: 1000 * 60 * 20}
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
    if (data.length > 0) {
        return (
            <Grid container spacing={3}>
                {
                    data.map(postElement => (
                        <ResultItem key={postElement.id} post={{
                            title: postElement.title,
                            date: postElement.updated,
                            description: postElement.description,
                            url: `/${searchRange}/${postElement.id}`
                        }}/>
                    ))
                }
            </Grid>
        );
    } else {
        return (
            <Typography>
                Can't find any result
            </Typography>
        );
    }

}

export default function Search() {
    const classes = useStyles();

    const [pageId, setPageId] = React.useState(1);
    const modifyPageId = (newPageId) => {
        if (newPageId <= 1) {
            setPageId(1);
        } else {
            setPageId(newPageId);
        }
    };

    const [searchAccuracy, setSearchAccuracy] = React.useState('or');
    const handleSearchAccuracyChange = (event) => {
        console.log(`SearchAccuracy ${searchAccuracy} => ${event.target.value}`);
        setSearchAccuracy(event.target.value);
        modifyPageId(1);
    };

    const [similarWords, setSimilarWords] = React.useState('10');
    const handleSimilarWordsChange = (event) => {
        setSimilarWords(event.target.value);
        modifyPageId(1);
    };

    const [searchRange, setSearchRange] = React.useState("imagelist");
    const handleSearchRangeChange = (event) => {
        setSearchRange(event.target.value);
        modifyPageId(1);
    };

    const [pageSize, setPageSize] = React.useState(20);
    const handleChangePageSize = (event) => {
        console.log(`PageSize ${pageSize} => ${event.target.value}`);
        setPageSize(event.target.value);
        modifyPageId(1);
    }

    const [searchKeywords, setSearchKeywords] = React.useState("");
    const [query, setQuery] = React.useState(searchKeywords);

    const handleSearchKeywords = (event) => {
        setSearchKeywords(event.target.value);
    };

    const handleClickSearch = () => {
        console.log(`Query ${query} => ${searchKeywords}`);
        setQuery(searchKeywords);
        modifyPageId(1);
    }

    const handleTextKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleClickSearch()
        }
    }


    return (
        <Container maxWidth="lg">
            <br/>
            <Grid container spacing={3}>
                <Grid item xs={10}>
                    <TextField
                        variant="filled"
                        className={{
                            margin: theme.spacing(1),
                        }}
                        id="search-keywords"
                        label="Search"
                        fullWidth
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <Select
                                        id="search-range"
                                        value={searchRange}
                                        onChange={handleSearchRangeChange}
                                        className={classes.rangeSelect}
                                    >
                                        <MenuItem value={"imagelist"}><ImageIcon/></MenuItem>
                                        <MenuItem value={"videolist"}><VideoLibraryIcon/></MenuItem>
                                        <MenuItem value={"novel"}><MenuBookIcon/></MenuItem>
                                    </Select>
                                </InputAdornment>
                            )
                        }}
                        value={searchKeywords}
                        onChange={handleSearchKeywords}
                        onKeyPress={handleTextKeyPress}
                    >
                    </TextField>
                </Grid>
                <Grid item xs={2}>
                    <Button variant="contained" color="primary" fullWidth className={classes.searchButton}
                            onClick={handleClickSearch}>
                        <SearchIcon/>
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12}>
                    <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                        >
                            <Typography className={classes.heading}>Advanced Search</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid item xs={12} md={6} sm={6}>
                                <FormControl fullWidth>
                                    <InputLabel id="search-accuracy-select-label">Search Accuracy</InputLabel>
                                    <Select
                                        labelId="search-accuracy-select-label"
                                        id="search-accuracy"
                                        value={searchAccuracy}
                                        onChange={handleSearchAccuracyChange}
                                    >
                                        <MenuItem value={"or"}>Or</MenuItem>
                                        <MenuItem value={"andmaybe"}>And Maybe</MenuItem>
                                        <MenuItem value={"and"}>And</MenuItem>
                                        <MenuItem value={"contains"}>Contains</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={6} sm={6}>
                                <FormControl fullWidth>
                                    <InputLabel id="page-size-select-label">Results Per Page</InputLabel>
                                    <Select
                                        labelId="page-size-select-label"
                                        id="page-size"
                                        value={pageSize}
                                        onChange={handleChangePageSize}
                                    >
                                        <MenuItem value={20}>20</MenuItem>
                                        <MenuItem value={50}>50</MenuItem>
                                        <MenuItem value={100}>100</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={6} sm={6}>
                                <FormControl fullWidth>
                                    <InputLabel id="similar-words-select-label">Similar Words</InputLabel>
                                    <Select
                                        labelId="similar-words-select-label"
                                        id="similar-words"
                                        value={similarWords}
                                        onChange={handleSimilarWordsChange}
                                    >
                                        <MenuItem value={0}>0</MenuItem>
                                        <MenuItem value={1}>1</MenuItem>
                                        <MenuItem value={2}>2</MenuItem>
                                        <MenuItem value={5}>5</MenuItem>
                                        <MenuItem value={10}>10</MenuItem>
                                        <MenuItem value={20}>20</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </AccordionDetails>
                    </Accordion>
                </Grid>
            </Grid>

            <ContentSearchResults
                searchRange={searchRange}
                query={query}
                page={pageId}
                pageSize={pageSize}
                searchAccuracy={searchAccuracy}
                similarWords={similarWords}
            />

            <Grid container spacing={3}>
                <Grid item sm={12} md={12} lg={12} xs={12}>
                    <BottomNavigation>
                        <BottomNavigationAction label="First" icon={<FirstPageIcon/>} onClick={() => modifyPageId(1)}/>
                        <BottomNavigationAction label="Previous" icon={<NavigateBeforeIcon/>}
                                                onClick={() => modifyPageId(pageId - 1)}/>
                        <BottomNavigationAction label="Current" icon={<Icon>{pageId}</Icon>}/>
                        <BottomNavigationAction label="Next" icon={<NavigateNextIcon/>}
                                                onClick={() => modifyPageId(pageId + 1)}/>
                    </BottomNavigation>
                </Grid>
            </Grid>

        </Container>
    );
}
