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

if [ -e $CONFIGFILE ]; then 
    source $CONFIGFILE
    echo "Thanks for the tasty config options"
fi


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
        exit 0
    elif [ $arg == '--reset-db' ]; then
        echo "Ok, I'll reset the DB"
        export G_DB_RESET="TRUE"
    elif [ $arg == '--dirty' ]; then
        echo "Ok, I won't clean the source tree"
        export CLEAN_INSTALL="FALSE"
    elif [ $arg == '--inspire' ]; then
        echo "Ok, I'll install INSPIRE from the separate repo and use the  inspire conf"
        export G_INSPIRE="TRUE"
        export LOCAL_CONF=$INSPIRE_CONF
        export INVENIO_DB=$INSPIRE_DB
    fi
done


# give user a chance to quit:
echo "[INFO] GOING TO DESTROY YOUR INSPIRE DEMO SITE IN VERY FEW SECONDS!"
echo "[INFO] THIS IS YOUR LAST CHANCE TO INTERRUPT BY PRESSING Ctrl-C!"
for i in 0 1 ; do
    echo -n "."
    sleep 1
done
echo

sudo -v; 
# Stop running bibsched so that we don't create zombies
sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/bibsched stop


if [ $CLEAN_INSTALL == "TRUE" ]; then
    sudo rm -rf $CFG_INVENIO_PREFIX; 
    cd $INSPIRE_REPO
    git status
    echo "[INFO] I WILL REMOVE ALL UNTRACKED FILES ABOVE"
    echo "[INFO] STOP ME BY PRESSING Ctrl-C!"
    for i in 0 1 2 3; do
        echo -n "."
        sleep 1
    done
    sudo git clean -x -f;
    cp $CFG_INSPIRE_DIR/config-local.mk .
    cd $INVENIO_REPO
    git status
    echo "[INFO] I WILL REMOVE ALL UNTRACKED FILES ABOVE"
    echo "[INFO] STOP ME BY PRESSING Ctrl-C!"
    for i in 0 1 2 3; do
        echo -n "."
        sleep 1
    done
    sudo git clean -x -f;
    aclocal && automake -a -c && autoconf -f && ./configure $CONFIGURE_OPTS  0</dev/null 
fi
 
cd $INVENIO_REPO
make && sudo make install \
    && sudo chown -R $CFG_INVENIO_USER:$CFG_INVENIO_USER $CFG_INVENIO_PREFIX \
    && sudo install -m 660 -o $CFG_INVENIO_USER -g $CFG_INVENIO_USER $LOCAL_CONF $CFG_INVENIO_PREFIX/etc/invenio-local.conf; 
if [ $? -eq 0 ]; then
    echo -e "\n** INVENIO INSTALLED SUCCESSFULLY\n";
else
    exit 1;
fi

sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --update-all 

if [ $? -eq 0 ]; then
  echo -e "\n** CONFIGURATION UPDATED SUCCESSFULLY\n"; 
else
  exit 1;
fi

if [ $INSTALL_PLUGINS == "TRUE" ]; then
    echo -e "INSTALLING \"OPTIONAL\" COMPONENTS...";
    sudo -u $CFG_INVENIO_USER make install-mathjax-plugin
    sudo -u $CFG_INVENIO_USER make install-jquery-plugins
#sudo -u $CFG_INVENIO_USER make install-fckeditor-plugin
#sudo -u $CFG_INVENIO_USER make install-pdfa-helper-files
fi


if [ $G_INSPIRE = 'TRUE' ]; then
    echo -e "Installing INSPIRE from repo $INSPIRE_REPO"
    cd $INSPIRE_REPO
    sudo make install
    sudo chown -R $CFG_INVENIO_USER:$CFG_INVENIO_USER $CFG_INVENIO_PREFIX
    echo "DONE."
fi


if [ $G_DB_RESET == 'TRUE' ]; then
    echo -e "DROPPING AND RECREATING THE DATABASE...";
    echo "drop database $INVENIO_DB;" | mysql -u root --password=$MYSQL_ROOT_PASS; 
    echo "CREATE DATABASE $INVENIO_DB DEFAULT CHARACTER SET utf8; GRANT ALL PRIVILEGES ON $INVENIO_DB.* TO $INVENIO_DB_USER@localhost IDENTIFIED BY '$INVENIO_DB_PASS';" | mysql -u root --password=$MYSQL_ROOT_PASS; 
    echo "DONE.";

    echo -e "SETTING UP THE INVENIO TABLES AND DEMO SITE..."
    sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --create-tables \
    && echo -e "\n** MYSQL TABLES CREATED SUCCESSFULLY\n" \
    && sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --load-webstat-conf \
    && echo -e "\n** WEBSTAT CONF LOADED SUCCESSFULLY\n" 
    sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --create-demo-site
    echo -e "\n** DEMO SITE INSTALLED\n"


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
       echo -e "\n** INSPIRE DEMO RECORDS INSTALLED"
       
   else
       sudo -u $CFG_INVENIO_USER $CFG_INVENIO_PREFIX/bin/inveniocfg --load-demo-records 
       echo -e "\n** DEMO RECORDS INSTALLED\n" 
       echo "DONE."
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
