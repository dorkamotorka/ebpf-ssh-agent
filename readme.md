# sshlog

SSHLog is a free, source-available Linux daemon written in C++ and Python that passively monitors OpenSSH servers via eBPF to:

  - **Record all SSH session activity** (commands and output) to log files for any connecting user
  - Allow administrators to **share an SSH session** with any logged in user
  - Watch SSH sessions and **post Slack messages** or run arbitrary commands when specific activity occurs
  - Forward all SSH events to a **remote syslog server**
  - Send **statsd metrics** to track user logins, disconnects, command activity, etc.
  - Configurable/Extendable **plug-in architecture** to execute custom actions triggered by SSH activity


SSHLog is configurable, any combination of features may be enabled, disabled, or customized.  It works with your existing OpenSSH server process, no alternative SSH daemon is required.  Just install the sshlog package to begin monitoring SSH.

![SSHLog header](http://www.sshlog.com/assets/img/hero/hero-img.png) 

## Quick Start

Install the daemon using the instructions for your OS (located below).  The default installation will:
  1. Install and enable the "sshlogd" daemon on startup
  2. Install the "sshlog" CLI application
  3. Enable a number of default configuration files in /etc/sshlog/conf.d/

    - /var/log/sshlog/event.log contains all SSH events: 
    - /var/log/sshlog/sessions/ log files contains all individual session activity (commands and output)

### After installation:

  - SSH into your server to generate some activity (e.g., ssh localhost).
  - Check log files in /var/log/sshlog/
    - /var/log/sshlog/event.log will contain a list of all actions (e.g., logins/logouts, commands run, files uploaded, etc)
    - /var/log/sshlog/sessions/ will contain the full shell terminal output, one file for each SSH session
  - Tip: Optionally add admin users to the "sshlog" group so that they can interact with SSHLog daemon without requiring sudo
  
Interact with the daemon via the CLI app:

#### Show current logged in sessions:

    mhill@devlaptop:~$ sshlog sessions
      
     User        Last Activity             Last Command               Session Start              Client IP           TTY
    mhill           just now              /usr/bin/gcc             2023-04-10 16:16:18        127.0.0.1:58668         17
    billy          10 min ago            /usr/sbin/fdisk           2023-04-10 12:11:05        15.12.5.8:58669         32


#### Monitor real-time SSH activity

    mhill@devlaptop:~$ sshlog watch
    
    16:16:45 connection_established (970236) billy from ip 15.12.5.8:59120 tty 33
    16:16:45 command_start          (970236) billy executed /bin/bash
    16:16:49 command_start          (970236) billy executed /usr/bin/whoami
    16:16:49 command_finish         (970236) billy execute complete (exit code: 0) /usr/bin/whoami
    16:16:51 command_start          (970236) billy executed /usr/bin/sudo ls
    16:16:54 command_start          (970236) billy executed /usr/bin/ls
    16:16:54 command_finish         (970236) billy execute complete (exit code: 0) /usr/bin/ls
    16:16:54 command_finish         (970236) billy execute complete (exit code: 0) /usr/bin/sudo ls
    16:16:56 command_finish         (970236) billy execute complete (exit code: 0) /bin/bash
    16:16:56 connection_close       (970236) billy from ip 15.12.5.8:59120

#### Attach to another user's shell session (either read-only or interactive)

    mhill@devlaptop:~$ sshlog attach [TTY ID]

    Attached to TTY 32.  Press CTRL+Q to exit

    billy@devlaptop:~$ 




### Debian/Ubuntu Install (arm64 and x86_64)

    apt update && apt install -y curl gnupg
    curl https://repo.sshlog.com/sshlog-ubuntu/public.gpg | gpg --yes --dearmor -o /usr/share/keyrings/repo-sshlog-ubuntu.gpg
    echo "deb [arch=any signed-by=/usr/share/keyrings/repo-sshlog-ubuntu.gpg] https://repo.sshlog.com/sshlog-ubuntu/ stable main" > /etc/apt/sources.list.d/repo-sshlog-ubuntu.list
    apt update && apt install -y sshlog



### RedHat/Fedora Install (arm64 and x86_64)

    echo """
    [sshlog-redhat]
    name=sshlog-redhat
    baseurl=https://repo.sshlog.com/sshlog-redhat
    enabled=1
    repo_gpgcheck=1
    gpgkey=https://repo.sshlog.com/sshlog-redhat/public.gpg
    """ > /etc/yum.repos.d/sshlog-redhat.repo
    yum update && yum install sshlog

### Docker Install (x86_64)

    # First, copy the default configuration files to the host /etc/sshlog directory
    # This step is unnecessary if you're using your own custom configuration
    id=$(docker create sshlog/agent:latest)
    docker cp $id:/etc/sshlog - > /tmp/sshlog_default_config.tar
    tar xvf  /tmp/sshlog_default_config.tar -C /etc/
    docker rm -v $id

    # Next create a detached container and volume mount 
    # the config files (/etc/sshlog) and output log files (/var/log/sshlog)
    # you could place the config files and log file volume mounts elsewhere if you prefer
    docker run -d --restart=always --name sshlog \
           --privileged \
           -v /sys:/sys:ro \
           -v /dev:/dev \
           -v /proc:/proc \
           -v /etc/passwd:/etc/passwd:ro \
           -v /var/log/sshlog:/var/log/sshlog \
           -v /etc/sshlog:/etc/sshlog \
           --pid=host \
           sshlog/agent:latest



## Configuration

The configuration files can be customized to trigger any number of actions based on configurable conditions.  For example:

  - Send a Slack message when an SSH login succeeds or fails
  - Trigger a script if anyone runs the "nmap" command.
  - Send an e-mail if a particular username uploads a file via scp

Active configurations are located in /etc/sshlog/conf.d/

Sample configurations for reference are located in /etc/sshlog/samples/ 

Detailed configuration documentation is available in the [daemon/config_samples/](daemon/config_samples/) folder


## Custom Plug-ins

SSHLog plug-in architecture supports running custom Python code to filter and act upon SSH events.  These plug-ins have full access to the SSH data and are triggered in real-time.  In fact, all of the core functionality available in SSHLog uses this same plug-in architecture.

To create your own plug-ins, follow along with the [documentation and tutorial  ](daemon/plugins/readme.md)


## Requirements

  - \*Linux Kernel 5.4 or higher (released Nov 2019)
  - OpenSSH server 1.8.1 or higher

\*SSHLog uses eBPF filters to monitor OpenSSH passively.  This technique requires a minimum Linux kernel version in order to function

Older versions of OpenSSH Server may work correctly, however it has not been tested
