# MSE Cloud lab 1
## Guillaume Hochet - Eric Tran - Olivier Kopp - Romain Silvestri - Anass Baddou

In this lab we chose to deploy an instance of Ejabberd along a MySQL database with a small Converse.JS frontend.

## Encountered problems with our application
We encountered multiple problems just deploying the application, thus common to everyone indepentently from the chosen cloud provider.

1. Ejabberd is no easy to setup correctly, we had to understand how it worked to be able to deploy it correctly.
2. Changing Ejabberd hosts (on which hosts he's listening) is really troublesome, it will provoke problems when restarting and registering a user. Solving this actually took me more time than the rest of the lab
3. Deploying the frontend required to upload an index.html file which we could overwrite later in the deployment phase. You can find it [here](https://gist.github.com/ovesco/f9c4474cceb6e5c358c3580f8b39fee7)

## Scripts
### Exoscale (Guillaume Hochet)
Exoscale support for images is not as established as for AWS or Google Cloud, the procedure is really complex. The script will thus automate the creation of the whole deployment by setting up everything using `user-data`. Please note that due to the problem (2) listed previously, the deployment might not end successful and we don't really know why.
