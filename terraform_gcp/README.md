# Using Terraform to Create a GCP Bucket

This project demonstrates how to create a GCP bucket using Terraform. It includes creating a service account in GCP, setting up Terraform configurations, and executing the Terraform plan to create resources in GCP.

**Prerequities**
- A GCP account
- Terraform installed
- Homebrew installed (macOS users)

## Setup and Configuration

### Creating a Service Account
1. Navigate to IAM & Admin in the GCP Console and select Service Accounts.
2. Click Create Service Account and fill in the service account details.
3. Assign the following roles to the service account:
   - Storage Admin
   - Bigquery Admin
   - Compute Admin
4. Click Done to create the service account.
5. In the Service Accounts page, find your new service account and click the three dots (menu icon) and select Manage Keys.
6. Click Add Key, then Create New Key, and select JSON as the key type.
7. Save the JSON key file in a secure location on your machine.
- an easy way is to create a file in a directory, and use `nano` command to copy the key into the file

#
### Terraform Configuration Files
`main.tf`

```python
# Terraform block specifies the required version and providers
terraform {
  required_providers {
    google = {
      source = "hashicorp/google" # Google Cloud provider source
      version = "5.13.0" # Specifying the provider version
    }
  }
}

# Provider block configures the specified provider, in this case, Google
provider "google" {
  credentials = file(var.credentials)  # Path to the JSON credentials file
  project = var.project # GCP project ID
  region = var.region # GCP region
}

# Resource block for creating a Google Cloud Storage bucket
resource "google_storage_bucket" "terraform-demo-bucket" {
  name = var.gcs_bucket_name # Name of the bucket
  location = var.location # Bucket location
  force_destroy = true # Allows bucket deletion with objects in it

  # Lifecycle rule to manage objects within the bucket
  lifecycle_rule {
    condition {
      age = 1 # Age in days to take action
    }
    action {
      type = "AbortIncompleteMultipartUpload" # Action type
    }
  }
}

# Resource block for creating a Google BigQuery dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_name # Dataset ID
  location = var.location # Dataset location
}
```
This is the main Terraform configuration file. It defines the required providers and declares the resources to be created.

**Original file can be found here:** [main.tf](main.tf)

`variables.tf`
```python
variable "credentials" {
  description = "My credentials"
  default     = "data/keys/my-creds.json"
}

variable "project" {
  description = "Project"
  default     = "radiant-psyche-403018"
}

variable "region" {
  description = "Region"
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "bq_dataset_name" {
  description = "Big Query Dataset"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "radiant-psyche-403018-terrabucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}
```
This file defines variables used in `main.tf`.

Original file can be found here: [variables.tf](variables.tf)

### Usage
To use this Terraform configuration:

1. Navigate to the directory containing your Terraform files.
2. Initialize Terraform with `terraform init`.
3. Apply the Terraform plan with `terraform apply` or `terraform plan` to confirm before using applying.

#
### Setting up SSH Access

1. Create an .ssh/ directory
2. Generate an ssh key. Default command:
```
ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048
```
Example command for this project:
```
ssh-keygen -t rsa -f gcp -C gzuz -b 2048
```
Note: there are to keys, ".pub" key can be shared, but keep the private key secure.
3. In the GCP console, navigate to compute engine > settings > add the public SSH key under metadata.
4. Run `cat gcp.pub` and paste the contents into the SSH key field in the GCP Console.

#
### Creating and Accessing a VM Instance
1. Navigate to virtual machines menu under compute engine and create an instance.
   - 1. Changed name
   - 2. Changed region
   - 3. Change machine type to e2-standard-4 (4vCPU, 16 GB memory)
   - 4. Selected ubuntu 20.04 lts image and 30 gb size for boot disk
2. Once created, copy the external IP.
3. Change to the directory containing the SSH key and connect using:
```bash
ssh -i file-name username@ip                                               
```
Example
```bash
ssh -i gcp gzuz@34.67.217.8                                               
```

#
### Installing Anaconda and Docker
- Install Anaconda:
``` bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
bash Anaconda3-2023.09-0-Linux-x86_64.sh 
```
Follow the prompts, and either log out and back in, or run `source .bashrc`.

To verify if it worked, "(base)" will show before the username:

![Alt text](data/images/image1.png)

- Install Docker
```bash
sudo apt-get update # updates the list of packages
sudo apt-get install docker.io
```

#
### Creating a `config` File
Creating a [config](.ssh/config) file for ease of access
```bash
Host de-prac
    HostName 34.67.217.8
    User gzuz
    IdentityFile ~/.ssh/gcp # must be in home directory for it to work
```

#
### Using VScode with Remote SSH
- Download remote SSH extension in VSCode.
- Open a remote window (green icon on the bottom left corner).
- In the pop-up menu, click connect to host
   - Since I already created the config file, the name for the vm will show up
- Clone the repository:
```
git clone https://github.com/eesahasan1/Data-Engineering-Repository.git

```

#
### Using Docker Without `sudo` in VM Instance
In order to run Docker in the VM instance without having to use sudo every time, follow these steps:
1. Create a Docker group:
```
sudo groupadd docker
```
2. Add user to the Docker group
```
sudo gpasswd -a $USER docker
```
Example:
```
sudo gpasswd -a $gzuz docker
```
3. Restart the Docker service to apply these changes:
```
sudo service docker restart
```
4. Verify these changes:
![Alt text](data/images/image2.png)

#
### Downloading and Setting Up Docker Compose
1. Make a bin directoy `mk dir` to store the docker compose file
2. Change to the bin directory and download docker-compose:
```bash
wget https://github.com/docker/compose/releases/download/v2.24.3/docker-compose-linux-x86_64 -O docker-compose
```
3. Make the docker-compose fil executable:
```bash
chmod +x docker-compose
```
4. Run to check version
```bash
./docker-compose version
```
5. Add ~/bin to PATH for easy access to executables. Run `nano .bashrc` from home directory, then add the following:
```
export PATH="${HOME}/bin:${PATH}" 
```
> The `.bashrc` file is a script that runs every time a new terminal session is started in interactive mode using the Bash shell. It's one of the startup files used to configure a user's shell environment. `.bashrc` stands for "Bash run commands."

#
### Handling Docker Permission Error
When encountering this error after trying to run `docker-compose up -d`"
```bash
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/json?all=1&filters=%7B%22label%22%3A%7B%22com.docker.compose.config-hash%22%3Atrue%2C%22com.docker.compose.project%3Ddocker_sql%22%3Atrue%7D%7D": dial unix /var/run/docker.sock: connect: permission denied"
```

Run this command for a quick fix (note that it may introduce security risks):
```bash
sudo chmod 666 /var/run/docker.sock
```
This command changs file permissions:
chmod = change mode
666 = owner, group, others
- Permissions are represented as a three-digit numbers, where each digit can be a number from 0 to 7.
Each digit represents the permissions for different user classes:
  - The first digit is for the owner of the file.
  - The second digit is for the group associated with the file.
  - The third digit is for others (everyone else).

In other words:
- 4 always represents Read permission.
- 2 always represents Write permission.
- 1 always represents Execute permission.
  - Read (4) + Write (2) = 6: Grants read and write permissions.
  - Read (4) + Execute (1) = 5: Grants read and execute permissions.
  - Read (4) + Write (2) + Execute (1) = 7: Grants read, write, and execute permissions

**For a safer fix:**
```bash
sudo usermod -aG docker $USER
newgrp docker
sudo service docker restart
```
Example:
```bash
sudo usermod -aG docker $gzuz
```

#
### Installing and Using pgcli for Database Access In Terminal
`pgcli` is a command-line interface for Postgres that offers auto-completion and syntax highlighting. Follow these steps to install and use it:

1. Install pgcli using pip:

```bash
pip install pgcli
```
If the above command doesn't work, use conda:

```bash
conda install -c conda-forge pgcli
```

To access the database, run:

```bash
pgcli -h localhost -U root -d ny_taxi
```
- "-h" localhost specifies the host.
- "-U" root is the username for the database
- "-d" ny_taxi is the name of the database you are accessing.

To view running Docker containers enter `docker ps`

#
### Accessing pgAdmin Web Interface In a Container From the VM
1. Copy port information:
   - From the VM terminal, run `docker ps` and copy the port information of the container to be accessed.
2. Configure SSH in VSCode:
   - Open SSH interface in VSCode.
   - Paste the copied port information in the ports menu
3. Access via local machine:
   - Enter localhost:8080 in the local machines web browser to access the pgAdmin web interface.
4. Database Access
   - The database can also be accessed from the local machine's terminal using `pgcli -h localhost -U root -d ny_taxi`.

![!\[Alt text\](image.png)](data/images/image3.png)

#
### Running Jupyter Notebook in the VM for Data Ingestion
To use Jupyter Notebook hosted on the VM:

1. Run Jupyter Notebook:
   - In the VM terminal, run jupyter notebook.
   - Copy the provided link to access the Jupyter interface.
2. Add Port in VSCode:
   - Before using the link, add the port (typically 8888) in the SSH VSCode port menu.
3. Access Jupyter Interface:
   - Paste the Jupyter link into your web browser.
   - If a token is required, retrieve it with:
```
jupyter notebook list
```
- Example:
```
(base) gzuz@de-prac:~$ jupyter notebook list
Currently running servers:
http://localhost:8888/?token=094c20195b0cede1f232af980963c1fc77e93d16fe0973f8 :: /home/gzuz/Data-Engineering-Repository/docker_sql
```
Token: token=094c20195b0cede1f232af980963c1fc77e93d16fe0973f8
4. Installing `psycopg2-binary`:
- If there is a `ModuleNotFoundError: No module named 'psycopg2'` error when trying to connect to the engine, install the following:
```
pip install psycopg2-binary
```
- After installation, rerun the notebook.

#
### Installing terraform
There are two methods to install Terraform:
1. Direct download:
```bash
wget https://releases.hashicorp.com/terraform/1.7.1/terraform_1.7.1_linux_amd64.zip
```

2. Using a package manager (apt):\
When running it this way, `apt` (package manager) automatically places executable files in its standard location (system directory, not user directory) such as `/usr/bin` regardless of the current directory
```bash
 wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
 echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
 sudo apt update && sudo apt install terraform
```

#
### Configuring Google Cloud
To set up Google Cloud in the VM:
1. Transfer SSH key via sftp: 
 - Use `sftp` to transfer the SSH JSON key from local machine to the vm.

- Example:
```bash
sftp de-prac
mkdir .gc
put my-creds.json
```
2. Set environment variable:
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the transferred key.
- Example:
```
export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/my-creds.json
```
3. Activate google cloud service account
```
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

#
### Using Terraform
1. terraform init:
- initialize terraform
2. terraform plan:
- before using terraform plan, make sure the location for the SSH JSON key is correct
```
variable "credentials" {
  description = "My credentials"
  default     = "~/.gc/my-creds.json"
}
```
3. terraform apply

sudo shutdown now to stop the instance
when starting hte vm instance agian, copy the new external IP and replace the old one ine the SSH config file from the host machine. 
```
nano .ssh/config
```