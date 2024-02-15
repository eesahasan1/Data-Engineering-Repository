# Setting Up a Cloud Environment With GCP, Docker, and Terraform



## Table of Contents
1. [Overview](#overview)
1. [Setting up SSH Access](#setting-up-ssh-access)
1. [Creating and Accessing a VM Instance](#creating-and-accessing-a-vm-instance)
1. [Installing Anaconda and Docker](#installing-anaconda-and-docker)
1. [Simplifying Access with a config File](#simplifying-access-with-a-config-file)
1. [Using VScode with Remote SSH](#using-vscode-with-remote-ssh)
1. [Using Docker Without sudo in VM Instance](#using-docker-without-sudo-in-vm-instance)
1. [Downloading and Setting Up Docker Compose](#downloading-and-setting-up-docker-compose)
1. [Handling Docker Permission Error](#handling-docker-permission-error)
1. [Installing and Using pgcli for Database Access In Terminal](#installing-and-using-pgcli-for-database-access-in-terminal)
1. [Accessing Containerized pgAdmin Web Interface in the VM](#accessing-containerized-pgadmin-web-interface-in-the-vm)
1. [Running Jupyter Notebook in the VM for Data Ingestion](#running-jupyter-notebook-in-the-vm-for-data-ingestion)
1. [Installing Terraform](#installing-terraform)
1. [Configuring Google Cloud](#configuring-google-cloud)
1. [Using Terraform](#using-terraform)
1. [Shutdown and Restarting](#shutdown-and-restarting)



## Overview

This project provides a detailed guide for setting up a cloud environment using Google Cloud Platform (GCP), Docker, and Terraform. It aims to streamline the process of cloud setup, ensuring secure access, automating infrastructure deployment, and facilitating scalable data workflows.

### Objective

- **Streamlined Cloud Setup**: Simplifies the process of setting up and accessing cloud environments.
- **Secure and Efficient Access**: Establishes secure SSH access to virtual machines and Docker containers to ensure data safety and operational efficiency.
- **Infrastructure Automation**: Leverages Terraform to automate the provisioning of cloud resources, minimizing manual effort and potential for error.
- **Scalable Data Workflows**: Demonstrates the creation of scalable data pipelines, from extraction and transformation to loading, employing modern cloud and data engineering practices.

### Key Features

- **Comprehensive SSH Configuration**: Steps on creating and managing SSH keys for secure access to cloud resources.
- **VM Instance Setup with Terraform**: Deployment of GCP virtual machines with configurations optimized for various use cases.
- **Container Management with Docker**: Insights into Docker setup for containerization, improving application consistency and deployment speed.
- **Data Engineering Workflows**: Examples of automating data extraction, transformation, and loading processes, showcasing the integration with GCP buckets, PostgreSQL, and BigQuery.



## Setting up SSH Access
Ensures secure and easy access to the virtual machines and containers.

**1. Create an SSH Directory**
Create a dedicated directory for SSH keys: `mkdir ~/.ssh`

**2. Generate an SSH Key:**

```bash
ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048
```
> https://cloud.google.com/compute/docs/connect/create-ssh-keys

- Example:
```
ssh-keygen -t rsa -f gcp -C gzuz -b 2048
```
> ***Note: there are two keys, ".pub" key can be shared, but the other must be kept private.***

**3. Add SSH Key to GCP**

- Display the public key using cat ~/.ssh/KEY_FILENAME.pub.
- In GCP Console, navigate to Compute Engine > Metadata and add the public SSH key.



## Creating and Accessing a VM Instance
Creating a VM instance.

**1. Terraform Configuration**
- The following Terraform configuration was used to set up the VM with all the necessary options and dependencies:

```bash
# Resource block for creating a virtual machine (VM) instance on Google Cloud Platform (GCP)
resource "google_compute_instance" "de-prac" {
  
  # Configuration for the VM's boot disk (the primary disk containing the operating system)
  boot_disk {
    auto_delete = true  # Specifies that the boot disk will be automatically deleted when the VM is deleted, to avoid leaving unused disks.
    device_name = "de-prac"  # Assigns a name to the boot disk for identification purposes.

    # Parameters for initializing the boot disk with a specific image and settings
    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20240125"  # Specifies the operating system image for the disk, in this case, Ubuntu 20.04.
      size  = 30  # Sets the size of the boot disk to 30 GB, providing storage space for the OS and additional files.
      type  = "pd-balanced"  # Chooses a disk type that balances performance and cost, suitable for a variety of workloads.
    }

    mode = "READ_WRITE"  # Allows the disk to be both read from and written to, enabling normal operation of the VM.
  }

  # General settings for the VM instance
  can_ip_forward      = false  # Disables IP forwarding, which is related to routing and forwarding rules within the VM.
  deletion_protection = false  # Allows the VM to be deleted without additional protections, making it easier to manage resources.
  enable_display      = false  # Disables any attached display devices, as this VM is likely managed remotely or doesn't require a GUI.

  # Labels are key-value pairs that help organize and categorize resources within Google Cloud.
  labels = {
    goog-ec-src = "vm_add-tf"  # Example label to identify the source or purpose of the VM.
  }

  machine_type = "e2-standard-4"  # Specifies the VM's hardware configuration, with "e2-standard-4" indicating a standard machine type with 4 vCPUs and 16 GB of memory.

  name = "de-prac"  # The name of the VM instance, used to identify it within the Google Cloud project.

  # Network interface configuration, defining how the VM connects to the network and the internet
  network_interface {
    # Access configuration for the network interface, primarily related to external internet access
    access_config {
      network_tier = "PREMIUM"  # Selects the PREMIUM network tier for higher performance networking features.
    }

    queue_count = 0  # Sets the number of packet mirroring queues to 0, as packet mirroring is not used in this configuration.
    stack_type  = "IPV4_ONLY"  # Specifies that only IPv4 addresses will be used for this VM, not IPv6.
    subnetwork  = "projects/radiant-psyche-403018/regions/us-central1/subnetworks/default"  # Defines the subnetwork within the VPC (Virtual Private Cloud) that the VM is connected to.
  }

  # Scheduling options for the VM, affecting how it behaves under certain conditions
  scheduling {
    automatic_restart   = true  # Allows the VM to automatically restart if it crashes or is otherwise stopped unexpectedly.
    on_host_maintenance = "MIGRATE"  # VM is migrated to another host in the event of maintenance, rather than being stopped.
    preemptible         = false  # Indicates that the VM is not preemptible, meaning it won't be automatically terminated by Google Cloud to free up resources.
    provisioning_model  = "STANDARD"  # Uses the standard provisioning model, as opposed to a custom or specialized option.
  }

  # Service account and permissions for the VM, defining what Google Cloud services and resources the VM can access
  service_account {
    email  = "294191629607-compute@developer.gserviceaccount.com"  # The service account associated with the VM, used for authentication and authorization.
    scopes = [  # Defines the access scopes or permissions for the service account, limiting what resources and services the VM can interact with.
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append"
    ]
  }

  # Configuration for shielded VM options, enhancing the security of the VM
  shielded_instance_config {
    enable_integrity_monitoring = true  # Monitors the VM for changes to its boot integrity, helping detect malicious tampering.
    enable_secure_boot          = false  # Secure boot is not enabled, but when true, it ensures the VM only boots signed software.
    enable_vtpm                 = true   # Enables a virtual Trusted Platform Module (vTPM), which securely stores cryptographic keys.
  }

  zone = "us-central1-a"  # Specifies the Google Cloud zone where the VM will be created, affecting its physical location and availability.
}
```

> ***Refer to the [GCP configuration terraform file](main.tf) without comments***

**2. Alternatively, Manually Configure the VM**

- Navigate to the Virtual Machines menu under Compute Engine in GCP and create an instance with the desired specifications.
1. Changed name
2. Changed region
3. Change machine type to e2-standard-4 (4vCPU, 16 GB memory)
4. Selected Ubuntu 20.04 LTS image and 30 GB boot disk

**3. SSH Connection**
- Once the setup is complete, copy the external IP of the VM.
- Connect to the VM using SSH with the generated key:

```bash
ssh -i file-name username@ip                                               
```

- Example:
```bash
ssh -i gcp gzuz@34.67.217.8                                               
```

> ***The command `ssh -i file-name username@ip` is used in Unix-like systems to securely connect to a remote server using SSH (secure shell). The `-i` option specifies a private key for authentication, `username` is the user on the remote server, and `ip` is the server's IP address or hostname.***



## Installing Anaconda and Docker
Set up Anaconda for data science/analytics environment, and Docker for container management.

- Install Anaconda:

``` bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
bash Anaconda3-2023.09-0-Linux-x86_64.sh 
```

- Follow the installation prompts, and then either log out and back in, or run `source .bashrc` to apply changes.

- To verify if it worked, "(base)" will show before the username:

![Alt text](data/images/image1.png)

- Install Docker:

Update the package list and install Docker:
```bash
sudo apt-get update # updates the list of packages
sudo apt-get install docker.io
```



## Simplifying Access with a `config` File
Creating a [config](.ssh/config) file will make it easier and quicker to access the environment:

```bash
Host de-prac
    HostName 34.67.217.8
    User gzuz
    IdentityFile ~/.ssh/gcp # must be in home directory for it to work
```



## Using VScode with Remote SSH
Use VSCode's Remote SSH extension for streamlined code management.

**1. Download Remote SSH extension in VSCode.**

**2. Connect to the VM**

- Since the config file is already created, the name for the VM will show up.

**3. Clone the repository:**

- After entering the remote environment, clone the repo:
```bash
git clone https://github.com/eesahasan1/Data-Engineering-Repository.git
```



## Using Docker Without `sudo` in VM Instance
Add your user to the Docker group to run Docker commands without sudo.

**1. Create a Docker Group and Add User:**
```bash
sudo groupadd docker
sudo gpasswd -a $USER docker
```

- Example:
```bash
sudo gpasswd -a $gzuz docker
```

**2. Restart the Docker Service to Apply These Changes:**
```bash
sudo service docker restart
```

**3. Verify These Changes**

![Alt text](data/images/image2.png)



## Downloading and Setting Up Docker Compose
Download Docker Compose and make it executable for managing multi-container Docker applications.

**1. Make a `bin` Directory to Store the Docker Compose File**

```bash
mkdir ~/bin
cd ~/bin
wget https://github.com/docker/compose/releases/download/v2.24.3/docker-compose-linux-x86_64 -O docker-compose
```
**2. Make Executable and Verify**

- Grant execution rights and check the installed version:
```bash
chmod +x docker-compose
./docker-compose version
```

**OPTIONAL**

- Add ~/bin to PATH for easy access to executables. Run `nano .bashrc` from home directory and add the following:
```
export PATH="${HOME}/bin:${PATH}" 
```
> ***The `.bashrc` file is a script that runs every time a new terminal session is started in interactive mode using the Bash shell. It's one of the startup files used to configure a user's shell environment. `.bashrc` stands for "Bash run commands."***



## Handling Docker Permission Error
When encountering permission issues/error after trying to run `docker-compose up -d`, adjust permission or add user to the Docker group for a safer resolution:

- Run this command for a quick fix (note: it may introduce security risks):
```bash
sudo chmod 666 /var/run/docker.sock
```

- This command changs file permissions:\
**chmod** = change mode | 
**666** = owner, group, others
>
> Permissions are represented as a three-digit numbers, where each digit can be a number from 0 to 7.
Each digit represents the permissions for different user classes:
>  - The first digit is for the owner of the file.
>  - The second digit is for the group associated with the file.
>  - The third digit is for others (everyone else).
>       - 4 always represents Read permission.
>       - 2 always represents Write permission.
>       - 1 always represents Execute permission.
>        - Read (4) + Write (2) = 6: Grants read and write permissions.
>       - Read (4) + Execute (1) = 5: Grants read and execute permissions.
>       - Read (4) + Write (2) + Execute (1) = 7: Grants read, write, and execute permissions

- **For a safer fix:**
```bash
sudo usermod -aG docker $USER
newgrp docker
sudo service docker restart
```
> - `sudo usermod -aG docker $USER` adds the current user to the 'docker' group, granting them permission to run Docker commands without needing sudo.
> - `newgrp docker` switches the current session to use the 'docker' group, applying the new group membership immediately.
> - `sudo service docker restart` restarts the Docker service to ensure all changes take effect, including updating permissions and group memberships.

- Example:
```bash
sudo usermod -aG docker $gzuz
```



## Installing and Using pgcli for Database Access In Terminal
`pgcli` is a command-line interface for Postgres.

- Install pgcli using pip:

```bash
pip install pgcli
# or use conda if above does not work
conda install -c conda-forge pgcli
```

- To access the database, run:

```bash
pgcli -h localhost -U root -d ny_taxi
```
- "-h" localhost specifies the host.
- "-U" root is the username for the database
- "-d" ny_taxi is the name of the database you are accessing.

> To view running Docker containers enter `docker ps` or all containers `docker ps -a`



## Accessing Containerized pgAdmin Web Interface in the VM
Configure SSH in VSCode and access pgAdmin through the local machine's browser.

**1. Copy Port Information**
- From the VM terminal, run `docker ps` and copy the port information of the container to be accessed.

**2. Configure SSH in VSCode**
- Open SSH interface in VSCode.
- Paste the copied port information in the ports menu.

**3. Access via Local Machine**
- Enter localhost:8080 in the local machine's web browser to access the pgAdmin web interface.

**4. Database Access**
- The database can also be accessed from the local machine's terminal using `pgcli -h localhost -U root -d ny_taxi`.

![!\[Alt text\](image.png)](data/images/image3.png)



## Running Jupyter Notebook in the VM for Data Ingestion
Using Jupyter Notebook hosted on the VM.

**1. Run Jupyter Notebook**
- In the VM terminal, run jupyter notebook.
- Copy the provided link to access the Jupyter interface.

**2. Add Port in VSCode**
- Before using the link, add the port 8888 in the SSH VSCode port menu.

**3. Access Jupyter Interface**
- Paste the Jupyter link into the web browser.
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
> **Token:** token=094c20195b0cede1f232af980963c1fc77e93d16fe0973f8

**4. Installing `psycopg2-binary`**
- If there is a `ModuleNotFoundError: No module named 'psycopg2'` error when trying to connect to the engine, install `psycopg2-binary`:
```
pip install psycopg2-binary
```
**After installation, rerun the notebook.**



## Installing terraform
There are two methods to install Terraform:

**1. Direct Download**
```bash
wget https://releases.hashicorp.com/terraform/1.7.1/terraform_1.7.1_linux_amd64.zip
```

**2. Using a Package Manager**

- When running it this way, `apt` (package manager) automatically places executable files in its standard location (system directory, not user directory) such as `/usr/bin` regardless of the current directory
```bash
 wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
 echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
 sudo apt update && sudo apt install terraform
```



## Configuring Google Cloud
Setting up Google Cloud in the VM.

**1. Transfer SSH Key Via `sftp`** 
- Securely transfer your GCP service account key to the VM using `sftp`.

- Example:

```bash
sftp de-prac
mkdir .gc
put my-creds.json
```

**2. Set Environment Variable and Activate the Account:**

- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the transferred key, and activate the service account.

- Example:

```
export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/my-creds.json

gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```



## Using Terraform
Automate infrastructure deployment with Terraform.

**1. `terraform init`:**
- Initializes terraform

**2. `terraform plan`:**
- Make sure the location for the SSH JSON key is correct

- Example:

```
variable "credentials" {
  description = "My credentials"
  default     = "~/.gc/my-creds.json"
}
```

**3. `terraform apply`**
- Final step to apply confifurates for infrastucture management



## Shutdown and Restarting
- Use `sudo shutdown now` to stop the VM instance
- When starting the VM instance again, copy the new external IP and replace the old one in the SSH config file from the host machine. 
```
nano .ssh/config
```