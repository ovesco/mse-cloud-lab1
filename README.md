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

### SwitchEngine (Romain Silvestri)
This part of the laboratory was troublesome because of issues with Switch. The members of the group couldn't connect to the project using their Keystone credential which made the use of the SDK impossible. A lot of time was lost because of this issue. To fix it, the assistant created an API on which we could submit the code and that would launch it using his credential. With this method, it was possible to do the script. But several issues were still present on the API side with function simply not working.  
Because if this event, a lot of time was lost, hence the state of the script. This script create two of the 3 necessary instances in the cloud and launch the third one. The front and back-end are then assigned precreated floating ips so no further configuration of the instances was necessary. They were created from images and were already configured. This method was used to be able to submit a working script allowing to launch the application in the cloud without the need of executing commands on the machines. The drawback is that floating ips must be pre-created which increase the cost of the project.

### Microsoft Azure (Olivier Kopp)
For the automatic deployment, I used pre build images for the basic configuration. In addition, I used custom-data to change the config file on the backend (ejabberd.yml) and the index file on the frontend-end, according to the public ips allocated during provisioning. 
