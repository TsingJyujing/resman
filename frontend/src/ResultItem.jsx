import React from 'react';
import PropTypes from 'prop-types';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Hidden from '@material-ui/core/Hidden';

const useStyles = makeStyles({
    card: {
        display: 'flex',
    },
    cardDetails: {
        flex: 1,
    },
    cardMedia: {
        width: 160,
    },
});


/**
 *
 * @param {*} props
 *  Fields in props.post
 *      title:
 *      date:
 *      description:
 *      image:
 *      url:
 */
export default function ResultItem(props) {
    const classes = useStyles();
    const {post} = props;

    return (
        <Grid item xs={12} md={6} lg={6}>
            <CardActionArea component="a" href={post.url} target='_blank'>
                <Card className={classes.card}>
                    <div className={classes.cardDetails}>
                        <CardContent>
                            <Typography component="h2" variant="h5">
                                {post.title}
                            </Typography>
                            <Typography variant="subtitle1" color="textSecondary">
                                {post.date}
                            </Typography>
                            <Typography variant="subtitle1" paragraph>
                                {post.description}
                            </Typography>
                            <Typography variant="subtitle1" color="primary">
                                Continue...
                            </Typography>
                        </CardContent>
                    </div>
                    {"image" in post && <Hidden xsDown>
                        <CardMedia className={classes.cardMedia} image={post.image}/>
                    </Hidden>}
                </Card>
            </CardActionArea>
        </Grid>
    );
}

ResultItem.propTypes = {
    post: PropTypes.object,
};
