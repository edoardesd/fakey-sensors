
mergecap *.pcap  -w merged.pcap
argus -r merged.pcap -w merged.argus

ra -Lo -Rn merged.argus -s \
stime proto saddr sport daddr dport pkts spkts dpkts bytes sbytes dbytes dur load sload dload \
loss sloss dloss ploss psloss pdloss retrans sretrans dretrans pretrans rate srate drate \
dir state swin dwin tcprtt synack ackdat - tcp > argus.csv