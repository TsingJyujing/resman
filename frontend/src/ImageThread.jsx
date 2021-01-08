import React from 'react';
import LazyLoad from 'react-lazy-load';
import {makeStyles} from '@material-ui/core/styles';
import {Container} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";

const mockImages = [
    "2020-08-26-22-17-38.png",
    "2020-08-26-22-18-10.png",
    "2020-08-26-22-18-38.png",
    "2020-08-26-22-32-36.png",
    "2020-08-26-22-40-23.png",
    "2020-09-19-13-00-10.png",
    "2020-09-19-13-59-43.png",
    "2020-10-02-16-32-08.png",
    "2020-10-02-16-33-08.png",
    "2020-10-02-16-45-07.png",
    "2020-10-09-20-08-40.png",
    "2020-10-09-20-08-41.gif",
    "2020-10-09-20-14-20.png",
    "2020-10-09-20-15-33.png",
    "2020-10-09-20-20-02.png",
    "2020-10-09-20-21-06.png",
    "2020-10-09-20-23-00.png",
    "2020-10-09-20-25-39.png",
    "2020-10-09-20-26-27.png",
    "2020-10-09-20-27-29.png",
    "2020-10-09-20-27-42.png",
].map(
    fn => "https://raw.githubusercontent.com/TsingJyujing/blogs/master/img/" + fn
);

function Gallery({images}) {
    return (
        <Container maxWidth={"md"}>
            {images.map(image => {
                const [height, setHeightValue] = React.useState(300);
                const onContentVisible = () => {
                    setHeightValue("auto")
                };
                return (
                    <LazyLoad height={height} offsetVertical={300} onContentVisible={onContentVisible}>
                        <img src={image.src} alt={image.src} loading={"lazy"} width={"100%"}/>
                    </LazyLoad>
                )
            })}
        </Container>
    );
}

const useStyles = makeStyles((theme) => ({
    // User defined style here
}));

export default function ImageThread() {
    const classes = useStyles();
    return (
        <Container maxWidth={"lg"}>
            <br/>
            <Typography variant={"h4"} gutterBottom>
                Title of the thread
            </Typography>
            <Typography variant={"h6"} gutterBottom>
                Consequat mauris nunc congue nisi vitae suscipit. Fringilla est ullamcorper eget nulla
                facilisi etiam dignissim diam. Pulvinar elementum integer enim neque volutpat ac
                tincidunt. Ornare suspendisse sed nisi lacus sed viverra tellus. Purus sit amet volutpat
                consequat mauris. Elementum eu facilisis sed odio morbi. Euismod lacinia at quis risus sed
                vulputate odio. Morbi tincidunt ornare massa eget egestas purus viverra accumsan in. In
                hendrerit gravida rutrum quisque non tellus orci ac. Pellentesque nec nam aliquam sem et
                tortor. Habitant morbi tristique senectus et. Adipiscing elit duis tristique sollicitudin
                nibh sit. Ornare aenean euismod elementum nisi quis eleifend. Commodo viverra maecenas
                accumsan lacus vel facilisis. Nulla posuere sollicitudin aliquam ultrices sagittis orci a.
            </Typography>
            <Gallery images={
                mockImages.map(url => ({src: url}))
            }/>
        </Container>

    );
}
