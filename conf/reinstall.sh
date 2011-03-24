#!/bin/bash
# push-button installer for CDS invenio onto a carefully prepared RHEL5 host
#
# provides a perfectly clean installation free of legacy cruft on either the 
# filesystem or database

# CONFIGFILE should be a regular file in the home directory with the following 
# contents:
## INVENIO_DB="cdsinvenio"
## INVENIO_DB_USER="cdsinvenio"
## INVENIO_DB_PASS="some_invenio_password"
## MYSQL_ROOT_PASS="some_mysql_password"
## INSPIRE_REPO="/opt/inspire-old" (if needed)
## INSPIRE_DB="inspiretest" (if needed)
## INSPIRE_CONF="/opt/inspire/inspire-local.conf" (if needed)
## CFG_INVENIO_USER="apache"
## PREFIX="/opt/invenio"
# ...except without being commented out.
# 
# It must be readable only by the owner and have no other permissions

export CONFIGURE_OPTS="--with-python=/usr/bin/python"
export CFG_INSPIRE_DIR="/opt/inspire"
export CONFIGFILE="$CFG_INSPIRE_DIR/.invenio_install.conf"
export G_DB_RESET="FALSE"
export G_INSPIRE="FALSE"
export INVENIO_REPO="~/src/invenio/"
export INSPIRE_REPO="~/src/inspire/"
export INSPIRE_CONF="$CFG_INSPIRE_DIR/inspire-local.conf"
export LOCAL_CONF="$CFG_INSPIRE_DIR/invenio-local.conf"
export CFG_INVENIO_USER="apache"
export CFG_INVENIO_PREFIX="/opt/invenio"
export G_INSPIRE_DB="FALSE"
export APACHE_RESTART="sudo /etc/init.d/httpd restart"
export CLEAN_INSTALL="TRUE"
export USE_BIBCONVERT="FALSE"
export INSTALL_PLUGINS="FALSE"
export BE_QUIET="FALSE"

function say() {
    if [ $BE_QUIET == "FALSE" ]; then
        echo $@
    fi
    return 0
}

function warn_and_wait() {
    if [ $BE_QUIET == "TRUE" ]; then
        return 0;
    fi
    echo -ne $1
    for i in 0 1 2; do
        echo -n "."
        sleep 1
    done
    echo
}

function warn_and_remove_untracked_files() {
    local cleanargs="-q -x -f"
    if [ $BE_QUIET == "FALSE" ]; then
        git status
        warn_and_wait "[INFO] I WILL REMOVED ALL UNTRACKED FILES ABOVE\n[INFO] STOP ME BY PRESSING Ctrl-C!\n"
        cleanargs="-x -f"
    fi
    sudo git clean $cleanargs
}

for arg in $@; do
    if [ $arg == '--help' ]; then
        echo "You must have /opt/inspire/ with configuration files:"
        echo " .invenio-install.conf for me"
        echo " invenio-local.conf for invenio"
        echo " invenio-apache-vhost*.conf for apache"
        echo "And I won't blow away the MySQL database by default.  Inspect my source"
        echo "to learn what you need to know."
        echo "By default I will install invenio from a single repo"
        echo "call me with --inspire to also install an inspire repo"
        echo "By default I will clean temporary files from your repos"
        echo "call me with --dirty to leave those things alone"
        echo "use --reset-db to drop and create the requested db from scratch"
        echo ""
        echo "Sending --shutup will cause me to do my best to only report errors."
        echo "NB: on clean installs I will not warn you before removing files."
        exit 0
    elif [ $arg == '--shutup' ]; then
        export BE_QUIET="TRUE"         # Because silence is golden
    elif [ $arg == '--reset-db' ]; then
        say "Ok, I'll reset the DB"
        export G_DB_RESET="TRUE"
    elif [ $arg == '--dirty' ]; then
        say "Ok, I won't clean the source tree"
        export CLEAN_INSTALL="FALSE"
    elif [ $arg == '--inspire' ]; then
        say "Ok, I'll install INSPIRE from the separate repo and use the  inspire conf"
        export G_INSPIRE="TRUE"
        export LOCAL_CONF=$INSPIRE_CONF
        export INVENIO_DB=$INSPIRE_DB
    fi
done

if [ -e $CONFIGFILE ]; then 
    source $CONFIGFILE
    say "Thanks for the tasty config options"
fi


# give user a chance to quit, if it actually makes sense to do so:
if [ $CLEAN_INSTALL == "TRUE" ]; then
    warn_and_wait "[INFO] GOING TO DESTROY YOUR INSPIRE DEMO SITE IN VERY FEW SECONDS!\n[INFO] THIS IS YOUR LAST CHANCE TO INTERRUP BY PRESSING Ctrl-C!\n" 
fi

sudo -v; 
# Stop running bibsched so that we don't create zombies
sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibsched stop 1>/tmp/invenio_bibsched_stop.log


if [ $CLEAN_INSTALL == "TRUE" ]; then
    sudo rm -rf $CFG_INVENIO_PREFIX; 
    cd $INVENIO_REPO
    warn_and_remove_untracked_files
    say "** REGENERATING BUILD CONFIGURATION..."
    aclocal && automake -a -c && autoconf -f && ./configure $CONFIGURE_OPTS  0</dev/null 
    cd $INSPIRE_REPO
    warn_and_remove_untracked_files
    cp $CFG_INSPIRE_DIR/config-local.mk .
fi
 
cd $INVENIO_REPO
say "I won't produce output for a while so that I can go faster, but you may find"
say -e "something useful in some /tmp/invenio_\052.log files"        # \052 lets us echo a *
if [ $G_INSPIRE == "TRUE" ]; then
    say -e " and some /tmp/inspire_\052.log files";
fi
echo "."
make -j 1>/tmp/invenio_make.log && sudo make -j install 1>/tmp/invenio_make_install.log \
    && sudo chown -R $CFG_INVENIO_USER:$CFG_INVENIO_USER $CFG_INVENIO_PREFIX \
    && sudo install -m 660 -o $CFG_INVENIO_USER -g $CFG_INVENIO_USER $LOCAL_CONF $CFG_INVENIO_PREFIX/etc/invenio-local.conf; 
if [ $? -eq 0 ]; then
    say -e "\n** INVENIO INSTALLED SUCCESSFULLY\n";
else
    echo "Something went wrong during invenio installation."
    exit 1;
fi

sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --update-all 
if [ $? -eq 0 ]; then
    say -e "\n** CONFIGURATION UPDATED SUCCESSFULLY\n"; 
else
    echo "Something went wrong during inveniocfg update-all."
    exit 1;
fi

if [ $INSTALL_PLUGINS == "TRUE" ]; then
    if [ $CLEAN_INSTALL == "TRUE" ]; then
        say -n "INSTALLING \"OPTIONAL\" COMPONENTS...";
#sudo -u $CFG_INVENIO_USER make -j install-mathjax-plugin install-jquery-plugins install-fckeditor-plugin install-pdfa-helper-files 1>/tmp/invenio_make_install_plugins.log
        sudo -u $CFG_INVENIO_USER make -j install-mathjax-plugin install-jquery-plugins 1>/tmp/invenio_make_install_plugins.log
        if [ $? -eq 0 ]; then
            say " done.";
        else
            echo -e "\n ** WARNING ** Optional component installation encountered nonfatal errors.\n"
        fi
    fi
fi


if [ $G_INSPIRE = 'TRUE' ]; then
    say -n "Installing INSPIRE from repo $INSPIRE_REPO"
    cd $INSPIRE_REPO
    sudo make -j install 1>/tmp/inspire_make_install.log
    if [ $? -eq 0 ]; then
        say -e " done.\n** INSPIRE INSTALLED SUCCESSFULLY\n";
    else
        echo "Something went wrong during inspire installation."
        exit 1;
    fi
    sudo chown -R $CFG_INVENIO_USER:$CFG_INVENIO_USER $CFG_INVENIO_PREFIX
fi


if [ $G_DB_RESET == 'TRUE' ]; then
    say -e "DROPPING AND RECREATING THE DATABASE...";
    echo "drop database $INVENIO_DB;" | mysql -u root --password=$MYSQL_ROOT_PASS; 
    echo "CREATE DATABASE $INVENIO_DB DEFAULT CHARACTER SET utf8; GRANT ALL PRIVILEGES ON $INVENIO_DB.* TO $INVENIO_DB_USER@localhost IDENTIFIED BY '$INVENIO_DB_PASS';" | mysql -u root --password=$MYSQL_ROOT_PASS; 
    say "DONE.";

    say -e "SETTING UP THE INVENIO TABLES AND DEMO SITE..."
    sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --create-tables \
    && say -e "\n** MYSQL TABLES CREATED SUCCESSFULLY\n" \
    && sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --load-webstat-conf \
    && say -e "\n** WEBSTAT CONF LOADED SUCCESSFULLY\n" 
    sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --create-demo-site
    say -e "\n** DEMO SITE INSTALLED\n"


   if [ $G_INSPIRE == 'TRUE' ]; then
# FIXME: things seem to work better without dropping our demo site.  Why is this? 
#      sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --drop-demo-site --yes-i-know
#      echo -e "\n** DROPPED DEMO SITE\n" 
       
       cd $INSPIRE_REPO
       sudo -u $CFG_INVENIO_USER make install-dbchanges

       cd bibconvert
       if [ $USE_BIBCONVERT == "TRUE" ]; then
           make get-small
           make convert-small
           sudo -u $CFG_INVENIO_USER make upload-small
       else
           make get-small-marc
           sudo -u $CFG_INVENIO_USER make upload-small
       fi
       #FIXME when we get the inst xslt in place can move this into the
       #bibconvert
       make get-inst-marc
       sudo -u $CFG_INVENIO_USER make upload-inst
       
       cd ..
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibindex -u admin
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibreformat -u admin -o HB
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/webcoll -u admin
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibrank -u admin
       say -e "\n** INSPIRE DEMO RECORDS INSTALLED"
       
   else
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --load-demo-records 
       say -e "\n** DEMO RECORDS INSTALLED\n" 
       say "DONE."
    fi
fi


sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --create-apache-conf 

# save aside the last confs just in case we are interested
if [ ! -d $CFG_INSPIRE_DIR/last_generated_conf/ ]; then
    sudo mkdir -v $CFG_INSPIRE_DIR/last_generated_conf/
fi
sudo cp -v $CFG_INVENIO_PREFIX/etc/apache/*conf $CFG_INSPIRE_DIR/last_generated_conf/

# but use the known working versions we store in /opt/inspire
for file in $CFG_INSPIRE_DIR/invenio-apache-vhost*.conf; do
    if [ -e $file ]; then
        sudo install -p -m 660 -g $CFG_INVENIO_USER -o $CFG_INVENIO_USER \
            $file $CFG_INVENIO_PREFIX/etc/apache         
    fi
done

$APACHE_RESTART

if [ $? -eq 0 ]; then
  echo -e "\n** APACHE SET UP CORRECTLY\n";
else
  exit 1;
fi


#echo -e "\nOk, now everything should work.\nInstalling a cron job for feedbox updates...."
#echo -e "\n3,23,46 * * * * $CFG_INVENIO_PREFIX/bin/inspire_update_feedboxes -d\n" >>/tmp/apache_entry
#sudo cat /var/spool/cron/apache /tmp/apache_entry >/tmp/apache_cron
#sudo mv /tmp/apache_cron /var/spool/cron/apache && sudo chmod 600 /var/spool/cron/apache
#echo -e " done.\nPlease cat /var/spool/cron/apache to make sure I didn't\n"
#echo -e "accidentally create multiple entries.\n"

if [ $G_INSPIRE == "TRUE" ]; then
    sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inspire_update_feedboxes.py -d
fi


echo -e "\nSo we've gotten this far, let's try starting the standard system\nservices, such as webcoll.\n"

#start fresh bibsched process (not positive this works - may still pick up
#old processes)
sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibsched start
sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/webcoll -u admin



exit 0
