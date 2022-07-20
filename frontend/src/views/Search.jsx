import React, {useState} from 'react';

import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import SearchIcon from "@material-ui/icons/Search";

import {makeStyles} from '@material-ui/core/styles';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    CircularProgress,
    Container,
    FormControl,
    Grid,
    IconButton,
    InputAdornment,
    InputLabel,
    MenuItem,
    Select,
    TextField,
    Typography
} from '@material-ui/core';
import {useQuery} from "react-query";

import ResultItem from "../components/ResultItem";
import theme from "../theme";
import {createGetRequestUrl} from "../Utility";
import useQueryString from "../components/useQueryString";
import {Paginator} from "../components/Paginator";

const useStyles = makeStyles((theme) => ({
    heading: {
        fontSize: theme.typography.pxToRem(15),
        fontWeight: theme.typography.fontWeightRegular,
    },
    rangeSelect: {
        height: "39px"
    }
}));

function SearchExplanation({query, similarWords}) {
    const queryCondition = {
        "q": query,
        "sw": similarWords
    };
    const {isLoading, error, data} = useQuery(
        `Explain Search(${JSON.stringify(queryCondition)})`,
        () => fetch(
            createGetRequestUrl(
                `/api/nlp/query_expand`,
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
    return (
        <Container maxWidth="lg">
            {Object.entries(data).filter(kv => kv[0] !== "").map(kv => {
                return (<Typography>
                    {`${kv[0]} -> ${kv[1].map(o => `${o["word"]}(${o["score"].toFixed(3)})`).join("/")}`}
                </Typography>)
            })}
        </Container>
    );
}

function ContentSearchResults({searchRange, query, page, pageSize, searchAccuracy, similarWords, likedOnly, orderBy, cacheKey}) {

    const queryCondition = {
        "p": page,
        "n": pageSize,
        "sw": similarWords,
        "ord": orderBy,
    };
    if (query !== "") {
        queryCondition["q"] = query;
        queryCondition["a"] = searchAccuracy;
    }
    if (likedOnly) {
        queryCondition["lo"] = "true"
    }
    const {isLoading, error, data} = useQuery(
        `Query(${searchRange})(${JSON.stringify(queryCondition)})/${cacheKey}`,
        () => fetch(
            createGetRequestUrl(
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
            <Grid container spacing={1}>
                {
                    data.map(postElement => (
                        <ResultItem key={postElement.id} post={{
                            title: postElement.title,
                            date: postElement.updated || "-",
                            description: postElement.description || "-",
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

/**
 *
 * @param name Display name of search rangek
 * @param searchRange which range to search, videos/novels/...
 * @returns {JSX.Element}
 * @constructor
 */
export default function Search({name, searchRange}) {
    const classes = useStyles();

    const [pageId, setPageId] = useQueryString("p", "1");
    const resetPageId = () => setPageId("1");

    const [searchAccuracy, setSearchAccuracy] = useQueryString("a", 'contains_or');
    const handleSearchAccuracyChange = (event) => {
        setSearchAccuracy(event.target.value);
        handleClickSearch();
    };

    const [likedOnly, setLikedOnly] = useQueryString("lo", false);
    const handleChangeLikedOnly = (event) => {
        setLikedOnly(event.target.value);
        handleClickSearch();
    };

    const [similarWords, setSimilarWords] = useQueryString("sw", '5');
    const handleSimilarWordsChange = (event) => {
        setSimilarWords(event.target.value);
        handleClickSearch();
    };

    const [pageSize, setPageSize] = useQueryString("n", 20);
    const handleChangePageSize = (event) => {
        setPageSize(event.target.value);
        handleClickSearch();
    }

    const [query, setQuery] = useQueryString("q", "");
    const [searchKeywords, setSearchKeywords] = React.useState(query);

    const [cacheKey, setCacheKey] = useState(1);
    const resetCacheKey = ()=>setCacheKey(cacheKey+1)


    const [orderBy, setOrderBy] = useQueryString("ord", "default");

    const handleChangeOrderBy = (event) => {
        setOrderBy(event.target.value);
        handleClickSearch();
    };

    const handleSearchKeywords = (event) => {
        setSearchKeywords(event.target.value);
        resetPageId();
    };

    const handleClickSearch = () => {
        setQuery(searchKeywords);
        resetPageId();
        resetCacheKey();
    }

    const handleTextKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleClickSearch()
        }
    }

    document.title = `Search for ${name}`;

    return (
        <Container maxWidth="lg">
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <TextField
                        variant="filled"
                        className={{
                            margin: theme.spacing(1),
                        }}
                        id="search-keywords"
                        label={`Search for ${name}`}
                        fullWidth
                        value={searchKeywords}
                        onChange={handleSearchKeywords}
                        onKeyDown={handleTextKeyPress}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        aria-label="search the item"
                                        onClick={handleClickSearch}
                                        edge="end"
                                    >
                                        <SearchIcon onClick={handleClickSearch}/>
                                    </IconButton>
                                </InputAdornment>
                            )
                        }}
                    >
                    </TextField>
                </Grid>
                <Grid item xs={12}>
                    <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                        >
                            <Typography className={classes.heading}>Advanced Search</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid container spacing={1}>
                                <Grid item xs={12} md={6} lg={4}>
                                    <FormControl fullWidth>
                                        <InputLabel id="search-accuracy-select-label">Search Accuracy</InputLabel>
                                        <Select
                                            labelId="search-accuracy-select-label"
                                            id="search-accuracy"
                                            value={searchAccuracy}
                                            onChange={handleSearchAccuracyChange}
                                        >
                                            <MenuItem value={"or"}>Or(Full Text)</MenuItem>
                                            <MenuItem value={"andmaybe"}>AndMaybe(Full Text)</MenuItem>
                                            <MenuItem value={"and"}>And(Full Text)</MenuItem>
                                            <MenuItem value={"contains_and"}>And(Title Contains)</MenuItem>
                                            <MenuItem value={"contains_or"}>Or(Title Contains)</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6} lg={4}>
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
                                <Grid item xs={12} md={6} lg={4}>
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
                                <Grid item xs={12} md={6} lg={4}>
                                    <FormControl fullWidth>
                                        <InputLabel id="liked-only-select-label">Search Liked Items</InputLabel>
                                        <Select
                                            labelId="liked-only-select-label"
                                            id="liked-only"
                                            value={likedOnly}
                                            onChange={handleChangeLikedOnly}
                                        >
                                            <MenuItem value={false}>Search All Items</MenuItem>
                                            <MenuItem value={true}>Search Liked Items Only</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6} lg={4}>
                                    <FormControl fullWidth>
                                        <InputLabel id="order-by-select-label">Order By</InputLabel>
                                        <Select
                                            labelId="order-by-select-label"
                                            id="order-by"
                                            value={orderBy}
                                            onChange={handleChangeOrderBy}
                                        >
                                            <MenuItem value={"default"}>Default(- Create Timestamp)</MenuItem>
                                            <MenuItem value={"lucky"}>Lucky(Random)</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} md={12} lg={12}>
                                    <Typography>Explanation</Typography>
                                    <SearchExplanation
                                        query={query}
                                        similarWords={similarWords}
                                    />
                                </Grid>
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
                likedOnly={likedOnly}
                orderBy={orderBy}
                cacheKey={cacheKey}
            />

            <Paginator pageId={pageId} setPageId={setPageId}/>

        </Container>
    );
}
