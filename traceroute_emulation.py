#!/usr/bin/env python3

from ipmininet.clean import cleanup
from ipmininet.cli import IPCLI
from ipmininet.ipnet import IPNet
from ipmininet.iptopo import IPTopo
from ipmininet.router.config import ebgp_session, BorderRouterConfig
from ipmininet.srv6 import SRv6Encap


class AssignmentPaper(IPTopo):
    def __init__(self, srv6: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.srv6 = srv6

    def build(self, *args, **kwargs):
        h1 = self.addHost('h1')
        r1 = self.addBGPRouter('r1')
        r2 = self.addBGPRouter('r2')

        h2 = self.addHost('h2')
        r3 = self.addBGPRouter('r3')
        r4 = self.addBGPRouter('r4')
        r5 = self.addBGPRouter('r5')
        r6 = self.addBGPRouter('r6')


        lh1r1 = self.addLink(h1, r1)
        lh1r1[h1].addParams(ip="2042:a1::a/64")
        lh1r1[r1].addParams(ip="2042:a1::1/64")

        lr1r2 = self.addLink(r1, r2)
        lr1r2[r1].addParams(ip="2042:12::1/64")
        lr1r2[r2].addParams(ip="2042:12::2/64")

        self.addiBGPFullMesh(2, (r1, r2))


        lr3r4 = self.addLink(r3, r4)
        lr3r4[r3].addParams(ip="2042:34::3/64")
        lr3r4[r4].addParams(ip="2042:34::4/64")

        lr3r5 = self.addLink(r3, r5)
        lr3r5[r3].addParams(ip="2042:35::3/64")
        lr3r5[r5].addParams(ip="2042:35::5/64")

        lr4r6 = self.addLink(r4, r6)
        lr4r6[r4].addParams(ip="2042:46::4/64")
        lr4r6[r6].addParams(ip="2042:46::6/64")

        lr6r5 = self.addLink(r6, r5)
        lr6r5[r6].addParams(ip="2042:65::6/64")
        lr6r5[r5].addParams(ip="2042:65::5/64")

        lr5h2 = self.addLink(r5, h2)
        lr5h2[r5].addParams(ip="2042:5b::5/64")
        lr5h2[h2].addParams(ip="2042:5b::b/64")

        self.addiBGPFullMesh(1, (r3, r4, r5, r6))


        lr2r3 = self.addLink(r2, r3)
        lr2r3[r2].addParams(ip="2042:23::2/64")
        lr2r3[r3].addParams(ip="2042:23::3/64")

        ebgp_session(self, r2, r3)

        self.addNetworkCapture(
            nodes=self.hosts() + self.routers(),
            base_filename="capture_traceroute",
            extra_arguments="-v")

        super(AssignmentPaper, self).build(*args, **kwargs)

    def addBGPRouter(self, name, **kwargs):
        return super().addRouter(name, config=BorderRouterConfig)

    def post_build(self, net):
        if self.srv6:
            SRv6Encap(net, node='r3', to='h2', through=['r6'], mode=SRv6Encap.ENCAP)
        super().post_build(net)


if __name__ == '__main__':
    net = IPNet(topo=AssignmentPaper(srv6=True), use_v4=False, use_v6=True,
                allocate_IPs=False)
    net.start()
    IPCLI(net)

    net.stop()
    cleanup()
