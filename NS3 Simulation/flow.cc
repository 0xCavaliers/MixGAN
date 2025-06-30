#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-helper.h"
#include "ns3/netanim-module.h"
#include "ns3/uinteger.h"
#include "ns3/string.h"
#include "ns3/double.h"
#include "ns3/boolean.h"
#include "ns3/nstime.h"
#include "ns3/udp-client.h"
#include "ns3/ptr.h"
#include "ns3/attribute.h"
#include "ns3/object-factory.h"
#include "ns3/data-rate.h"
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include "ns3/tag.h"

using namespace ns3;

// NS_LOG_COMPONENT_DEFINE("IoTSimulation"); 

struct MyEvent {
    uint32_t src;
    uint32_t dst;
    double start;
    double duration;
    uint32_t size;
    std::string proto;
    uint16_t port;
    std::string type;
};

class FlowMetaTag : public ns3::Tag {
public:
    std::string service;
    std::string attack_class;
    uint32_t srcNode;
    uint32_t dstNode;
    std::string proto;
    FlowMetaTag() {}
    FlowMetaTag(const std::string& s, const std::string& c, uint32_t src, uint32_t dst, const std::string& p)
        : service(s), attack_class(c), srcNode(src), dstNode(dst), proto(p) {}

    static ns3::TypeId GetTypeId() {
        static ns3::TypeId tid = ns3::TypeId("FlowMetaTag")
            .SetParent<ns3::Tag>()
            .AddConstructor<FlowMetaTag>();
        return tid;
    }
    virtual ns3::TypeId GetInstanceTypeId() const override { return GetTypeId(); }
    virtual uint32_t GetSerializedSize() const override {
        return service.size() + attack_class.size() + proto.size() + 3 * sizeof(uint32_t) + 3;
    }
    virtual void Serialize(ns3::TagBuffer i) const override {
        i.WriteU8(service.size());
        i.Write((const uint8_t*)service.c_str(), service.size());
        i.WriteU8(attack_class.size());
        i.Write((const uint8_t*)attack_class.c_str(), attack_class.size());
        i.WriteU8(proto.size());
        i.Write((const uint8_t*)proto.c_str(), proto.size());
        i.WriteU32(srcNode);
        i.WriteU32(dstNode);
    }
    virtual void Deserialize(ns3::TagBuffer i) override {
        uint8_t ssz = i.ReadU8();
        char s[64] = {0};
        i.Read((uint8_t*)s, ssz);
        service = std::string(s, ssz);
        uint8_t csz = i.ReadU8();
        char c[64] = {0};
        i.Read((uint8_t*)c, csz);
        attack_class = std::string(c, csz);
        uint8_t psz = i.ReadU8();
        char p[16] = {0};
        i.Read((uint8_t*)p, psz);
        proto = std::string(p, psz);
        srcNode = i.ReadU32();
        dstNode = i.ReadU32();
    }
    virtual void Print(std::ostream &os) const override {
        os << "service=" << service << ",class=" << attack_class << ",srcNode=" << srcNode << ",dstNode=" << dstNode << ",proto=" << proto;
    }
};

std::ofstream* g_detailLog = nullptr;
Ipv4InterfaceContainer* g_interfaces = nullptr;
uint32_t g_apNode = 0;

void ApPacketLogCallback(Ptr<const Packet> p, const Address &src, const Address &dst) {
    double now = Simulator::Now().GetSeconds();
    InetSocketAddress srcSockAddr = InetSocketAddress::ConvertFrom(src);
    InetSocketAddress dstSockAddr = InetSocketAddress::ConvertFrom(dst);
    std::ostringstream oss1, oss2;
    oss1 << srcSockAddr.GetIpv4();
    oss2 << dstSockAddr.GetIpv4();
    std::string srcIP = oss1.str();
    std::string dstIP = oss2.str();
    uint16_t srcPort = srcSockAddr.GetPort();
    uint16_t dstPort = dstSockAddr.GetPort();
    uint32_t size = p->GetSize();
    *g_detailLog << now << ",udp,-,-,-," << srcIP << "," << dstIP << "," << srcPort << "," << dstPort << "," << size << ",-\n";
}

void UdpPacketLogCallback(Ptr<const Packet> p, const Address &src, const Address &dst) {
    double now = Simulator::Now().GetSeconds();
    InetSocketAddress srcSockAddr = InetSocketAddress::ConvertFrom(src);
    InetSocketAddress dstSockAddr = InetSocketAddress::ConvertFrom(dst);
    std::ostringstream oss1, oss2;
    oss1 << srcSockAddr.GetIpv4();
    oss2 << dstSockAddr.GetIpv4();
    std::string srcIP = oss1.str();
    std::string dstIP = oss2.str();
    uint16_t srcPort = srcSockAddr.GetPort();
    uint16_t dstPort = dstSockAddr.GetPort();
    uint32_t size = p->GetSize();
    *g_detailLog << now << ",udp,-,-,-," << srcIP << "," << dstIP << "," << srcPort << "," << dstPort << "," << size << ",-\n";
}

void TcpPacketLogCallback(Ptr<const Packet> p, const Address &src, const Address &dst) {
    double now = Simulator::Now().GetSeconds();
    InetSocketAddress srcSockAddr = InetSocketAddress::ConvertFrom(src);
    InetSocketAddress dstSockAddr = InetSocketAddress::ConvertFrom(dst);
    std::ostringstream oss1, oss2;
    oss1 << srcSockAddr.GetIpv4();
    oss2 << dstSockAddr.GetIpv4();
    std::string srcIP = oss1.str();
    std::string dstIP = oss2.str();
    uint16_t srcPort = srcSockAddr.GetPort();
    uint16_t dstPort = dstSockAddr.GetPort();
    uint32_t size = p->GetSize();
    *g_detailLog << now << ",tcp,-,-,-," << srcIP << "," << dstIP << "," << srcPort << "," << dstPort << "," << size << ",-\n";
}

void TcpPacketLogCallback_Safe(Ptr<const Packet> p, const Address &src) {
    double now = Simulator::Now().GetSeconds();
    InetSocketAddress srcSockAddr = InetSocketAddress::ConvertFrom(src);
    std::ostringstream oss1;
    oss1 << srcSockAddr.GetIpv4();
    std::string srcIP = oss1.str();
    uint16_t srcPort = srcSockAddr.GetPort();
    uint32_t size = p->GetSize();
    *g_detailLog << now << ",tcp,-,-,-," << srcIP << ",10.1.0.1000," << srcPort << ",9999," << size << ",-\n";
}


void IcmpPacketLogCallback(Ptr<const Packet> p, const Address &src, const Address &dst) {
    double now = Simulator::Now().GetSeconds();
    InetSocketAddress srcSockAddr = InetSocketAddress::ConvertFrom(src);
    InetSocketAddress dstSockAddr = InetSocketAddress::ConvertFrom(dst);
    std::ostringstream oss1, oss2;
    oss1 << srcSockAddr.GetIpv4();
    oss2 << dstSockAddr.GetIpv4();
    std::string srcIP = oss1.str();
    std::string dstIP = oss2.str();
    uint16_t srcPort = srcSockAddr.GetPort();
    uint16_t dstPort = dstSockAddr.GetPort();
    uint32_t size = p->GetSize();
    *g_detailLog << now << ",icmp,-,-,-," << srcIP << "," << dstIP << "," << srcPort << "," << dstPort << "," << size << ",-\n";
}

int main(int argc, char *argv[])
{
    // Config::SetDefault("ns3::WifiPhy::HtSupported", BooleanValue(false)); 

    uint32_t numNodes = 1001; 
    double simulationTime = 60.0; 

    std::vector<MyEvent> events;
    std::ifstream fin("ns3_events.txt");
    std::string line;
    while (std::getline(fin, line)) {
        std::stringstream ss(line);
        MyEvent e;
        std::string size_str;
        std::vector<std::string> fields;
        std::string token;
        std::stringstream line_ss(line);
        while (std::getline(line_ss, token, ',')) {
            fields.push_back(token);
        }
        if (fields.size() < 8) {
            std::cerr << "Warning: Invalid line (too few fields), skipping: " << line << std::endl;
            continue;
        }
        try {
            e.src = std::stoul(fields[0]);
            e.dst = std::stoul(fields[1]);
            e.start = std::stod(fields[2]);
            e.duration = std::stod(fields[3]);
            e.size = std::stoul(fields[4]);
            e.proto = fields[5];
            e.port = static_cast<uint16_t>(std::stoul(fields[6]));
            e.type = fields[7];
        } catch (...) {
            std::cerr << "Warning: Error parsing line, skipping: " << line << std::endl;
            continue;
        }

        if (!e.proto.empty() && e.proto[0] == ' ') e.proto = e.proto.substr(1);
        if (!e.type.empty() && e.type[0] == ' ') e.type = e.type.substr(1);

        std::string proto_lower = e.proto;
        std::transform(proto_lower.begin(), proto_lower.end(), proto_lower.begin(), ::tolower);
        if ((proto_lower == "udp" || proto_lower == "icmp") && (e.size <= 0 || e.size > 65507)) {
            // std::cerr << "Info: UDP/ICMP event size auto-corrected from " << e.size << " to 64, line: " << line << std::endl;
            e.size = 64;
        }
        if (proto_lower == "tcp" && e.size <= 0) {
            // std::cerr << "Info: TCP event size auto-corrected from " << e.size << " to 1024, line: " << line << std::endl;
            e.size = 1024;
        }
        events.push_back(e);
    }

    NodeContainer nodes;
    nodes.Create(numNodes + 1); 
    NodeContainer wifiStaNodes;
    for (uint32_t i = 0; i < numNodes; ++i) wifiStaNodes.Add(nodes.Get(i));
    NodeContainer wifiApNode;
    wifiApNode.Add(nodes.Get(numNodes));

    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b); 
    wifi.SetRemoteStationManager("ns3::AarfWifiManager");

    WifiMacHelper mac;
    Ssid ssid = Ssid("iot-network");

    mac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid),
                "ActiveProbing", BooleanValue(false));
    NetDeviceContainer staDevices = wifi.Install(phy, mac, wifiStaNodes);

    mac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));
    NetDeviceContainer apDevice = wifi.Install(phy, mac, wifiApNode);

    NetDeviceContainer allDevices;
    for (uint32_t i = 0; i < staDevices.GetN(); ++i) allDevices.Add(staDevices.Get(i));
    for (uint32_t i = 0; i < apDevice.GetN(); ++i) allDevices.Add(apDevice.Get(i));

    MobilityHelper mobility;
    mobility.SetPositionAllocator("ns3::GridPositionAllocator",
                                  "MinX", DoubleValue(0.0),
                                  "MinY", DoubleValue(0.0),
                                  "DeltaX", DoubleValue(5.0),
                                  "DeltaY", DoubleValue(5.0),
                                  "GridWidth", UintegerValue(50),
                                  "LayoutType", StringValue("RowFirst"));
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(wifiStaNodes);
    mobility.Install(wifiApNode);

    InternetStackHelper stack;
    stack.Install(nodes);

    Ipv4AddressHelper address;
    address.SetBase("10.1.0.0", "255.255.0.0");
    Ipv4InterfaceContainer interfaces = address.Assign(allDevices);

    uint16_t defaultPort = 9999;
    UdpServerHelper udpServerHelper(defaultPort);
    ApplicationContainer serverApp = udpServerHelper.Install(nodes.Get(numNodes));
    serverApp.Start(Seconds(0.5));
    serverApp.Stop(Seconds(simulationTime));
    // TCP server
    PacketSinkHelper tcpSinkHelper("ns3::TcpSocketFactory", InetSocketAddress(interfaces.GetAddress(numNodes), defaultPort));
    ApplicationContainer tcpServerApp = tcpSinkHelper.Install(nodes.Get(numNodes));
    tcpServerApp.Start(Seconds(0.5));
    tcpServerApp.Stop(Seconds(simulationTime));

    // 动态调度流量
    for (auto e : events) {
        // Bounds check
        if (e.src >= nodes.GetN() || e.dst >= nodes.GetN()) {
            std::cerr << "Warning: Event src/dst out of range, skipping. src=" << e.src << ", dst=" << e.dst << std::endl;
            continue;
        }
        if (e.dst == 1000) e.dst = numNodes;
        std::string proto_lower = e.proto;
        std::transform(proto_lower.begin(), proto_lower.end(), proto_lower.begin(), ::tolower);
        if (proto_lower == "udp") {
            if (e.size < 12) e.size = 12;
            UdpClientHelper client(interfaces.GetAddress(e.dst), e.port);
            client.SetAttribute("MaxPackets", UintegerValue(1));
            client.SetAttribute("Interval", StringValue("1s"));
            client.SetAttribute("PacketSize", UintegerValue(e.size));
            double minDuration = 1.0;
            double stopTime = e.start + std::max(minDuration, e.duration);
            ApplicationContainer app = client.Install(nodes.Get(e.src));
            app.Start(Seconds(e.start));
            app.Stop(Seconds(stopTime));
        } else if (proto_lower == "tcp") {
            BulkSendHelper client("ns3::TcpSocketFactory", InetSocketAddress(interfaces.GetAddress(e.dst), e.port));
            client.SetAttribute("MaxBytes", UintegerValue(e.size));
            double minDuration = 1.0;
            double stopTime = e.start + std::max(minDuration, e.duration);
            ApplicationContainer app = client.Install(nodes.Get(e.src));
            app.Start(Seconds(e.start));
            app.Stop(Seconds(stopTime));
        } else if (proto_lower == "icmp") {
            OnOffHelper client("ns3::UdpSocketFactory", InetSocketAddress(interfaces.GetAddress(e.dst), e.port));
            client.SetAttribute("DataRate", StringValue("1Mbps"));
            client.SetAttribute("PacketSize", UintegerValue(e.size));
            double minDuration = 1.0;
            double stopTime = e.start + std::max(minDuration, e.duration);
            ApplicationContainer app = client.Install(nodes.Get(e.src));
            app.Start(Seconds(e.start));
            app.Stop(Seconds(stopTime));
        }
    }

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    g_detailLog = new std::ofstream("ap_rx_detail.csv");
    *g_detailLog << "Time,Protocol,Service,SrcNode,DstNode,SrcIP,DstIP,SrcPort,DstPort,Size,Class\n";
    g_interfaces = &interfaces;
    g_apNode = numNodes;

    Ptr<UdpServer> udpServerApp = serverApp.Get(0)->GetObject<UdpServer>();
    udpServerApp->TraceConnectWithoutContext("RxWithAddresses", MakeCallback(&ApPacketLogCallback));

    Ptr<PacketSink> tcpSinkApp = tcpServerApp.Get(0)->GetObject<PacketSink>();
    tcpSinkApp->TraceConnectWithoutContext("Rx", MakeCallback(&TcpPacketLogCallback_Safe));

    Simulator::Stop(Seconds(simulationTime));
    Simulator::Run();

    monitor->CheckForLostPackets();
    monitor->SerializeToXmlFile("flowmon.xml", true, true);

    // uint32_t totalRx = udpServerApp->GetReceived(); 
    // std::cout << "Total packets received by AP: " << totalRx << std::endl;

    Simulator::Destroy();

    g_detailLog->close();
    delete g_detailLog;
    return 0;
}
