## RIPE Network Tools ##

  * Added a new peer to your router ?
  * Forgot to update your aut-num following the change !
  * Save yourself time and automating the process.

## Disclaimer ##

The RIPE aut-num generation code is used on our network to parse juniper configurations. The parser does takes some shortcut when it comes to global definition and may not work for you (this will be fixed in a future release).

Cisco support was added, however as I do not have any EBGP cisco routers, so you may encounter bugs as the code can not be easily tested when I perform changes.

Do not hesitate to contact me if you have any questions, problems or think something is not as it should be:

whois -h whois.ripe.net -- "-B MANG-RIPE"

## How to use it ##

### Configure the software ###

The code searches for it's configuration options in the etc/network directory of the repository.

The syntax is one file per configuration option, the options should be self explanatory. eg: for running the ripe-juniper update code, the location of your locally saved Juniper configuration files is set by the contents of etc/network/juniper/backup.

The configuration files are:

For the folders juniper and cisco (relative to the configuration parsing):
  * backup : the location of your router configurations
  * customer : a list of the policy-statements / peer-goups used for customers, space separated
  * peer : a list of the policy-statements / peer-goups used for customers, space separated
  * transit : a list of the policy-statements / peer-goups used for transit, space separated
  * export : what connections to export in RIPE (customer, transit or peer),  space separated
  * multicast : the juniper code has no multicast parsing, so this is a temporary work-around
  * regex : the regex used to parse the peer description

For RIPE (for the RIPE object generation):
  * asn : your ASN, used to figure out what is eBGP/iBGP
  * company : Your company name
  * header : The mandatory information about your network (aut-num, as-name, description, admin-c, tech-c, etc.)
  * footer : like header but after all the import/export statements
  * macro : the ASN/AS-Macro to announce if nothing is specified in the peer description
  * production: true/false - are your ready to get the mails sent to RIPE
  * secret : the MD5 password RIPE has for your maintainer
  * sender : the from field for the mail to RIPE

(Should you want to use PGP signing just drop me a line and I will try to fight my lazyness and add the feature - the code for PGP signing is already written and used in other projects - I just need to integrate it in this one)

### Export/Backup your configuration ###

For Juniper just make sure you save your configuration to a local folder using the juniper archival feature, then edit the configuration file etc/network/juniper/backup to reflect this location.

The filename used when the file is FTP'd contains the date, allowing the tools to only work with the most recent configuration backup for each router.
```
   [edit system archival] 
   configuration {
       transfer-on-commit;
           archive-sites {
               "ftp://user:password@server/router-name/";
           }
       }
   }
```

For cisco routers, again save your configuration files locally and then edit etc/network/cisco/backup to reflect their location.

### Update your router configuration ###

Each of your neighbour description should have a peer-as set for the parser to work.

The regex matching this format is configurable, so you can adapt the tools to your existing format if you already have one.

The default regex expect a comment of the form:
```
   "AS-ACCEPTED | Peer name | noc@peer.co.uk | AS-SENT"
```
AS-SENT (or ASN), is optional as otherwise taken from the tools configuration, which is matched by the default regex:
```
    (?P<peer_accepted_asset>.*?)\|(?P<peer_name>.*?)\|(?P<peer_email>[^|]*)\|?(?P<peer_announced_asset>.*)
```
The type of connection is detected inspecting the export and import statement for special policy-options (or the peer-group on cisco).

An juniper example would be like follows:
```
   group transit {
       type external;
       local-preference 75;
       remove-private;
       neighbor 195.219.195.45 {
           description "ANY | Teleglobe / VSNL | email@vsnlinternational.com |";
           local-address 195.219.195.46;
           import [ no-ix no-bogons no-small-prefixes tag-transit tag-vsnl damping local-preference-transit no-community-import ];
           export [ originate-community originate-customer no-transit no-small-prefixes export-transit export-vsnl no-community-export next-hop-self ];
           peer-as 6453;
       }
   }
```
A cisco example would be like this:
```
   router bgp 12345
      bgp router-id 1.2.3.4
      bgp always-compare-med
      bgp log-neighbor-changes
      neighbor IBGP peer-group
      neighbor IBGP remote-as 12345
      neighbor IBGP update-source Loopback0
      neighbor PEER peer-group
      neighbor 9.8.7.6 remote-as 6789
      neighbor 9.8.7.6 peer-group PEER
      neighbor 9.8.7.6 description AS-ACCEPTED | Peer-Name | email@peer.com | AS-SENT
   !
   address-family ipv4
      no synchronization
      neighbor PEER send-community
      neighbor PEER soft-reconfiguration inbound
      neighbor PEER route-map PEER-IN in
      neighbor PEER route-map PEER-OUT out
      neighbor 9.8.7.6 activate
      neighbor 9.8.7.6 maximum-prefix 50 80 restart 15
      no auto-summary
      exit-address-family
   !
   address-family ipv6
      no synchronization
      neighbor PEER send-community
      neighbor PEER soft-reconfiguration inbound
      neighbor PEER route-map PEER-IN in
      neighbor PEER route-map PEER-OUT out
      neighbor 2001:1::1 activate
      neighbor 2001:1::1 maximum-prefix 50 80 restart 15
```

The code will parse the interface definition to figure the IP address used for the BGP connection.

Note: the IPv6 parsing code will only understand "simple" netmasks, ie: with boundaries on the IP hexadecimal characters (/4,/8,/12,/16,...,/120,/124,/128).

### Automate the process ###

You can now run a simple cron script to have this done every night for you.

### Usage example ###
```
[thomas@mac]$ ./bin/ripe-juniper
```
which is a shorter version of:
```
[thomas@mac]$ ./bin/locate-juniper -d | ./bin/parse-juniper | ./bin/export-ripe | ./bin/transmit-ripe
```
or could be to just print the content to the screen:
```
[thomas@mac]$ ./bin/locate-juniper ../../backup-folder | grep router-name | xargs cat | ./bin/parse-juniper -a 30740 -s AS-EXA -p export-ix-1 -p export-ix-2 -c export-customer -t export-transit | ./bin/export-ripe
```
Feel free to explore each program and its options.