import { Activity, AlertTriangle, CheckCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusCard } from "@/components/dashboard/StatusCard";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";

export default function Monitoring() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time system health and performance</p>
        </div>
        <Button className="bg-gradient-primary shadow-glow">
          <RefreshCw className="mr-2 h-4 w-4" />
          Run Health Check
        </Button>
      </div>

      {/* System Health Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-success/20 bg-success/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-success" />
                Operational Modules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-success">8</div>
              <Progress value={100} className="mt-2 bg-success/20" />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-warning/20 bg-warning/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Degraded Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-warning">2</div>
              <Progress value={20} className="mt-2 bg-warning/20" />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Overall Health Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">98.5%</div>
              <Progress value={98.5} className="mt-2" />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Module Status Grid */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Module Status</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <StatusCard
            title="Patient Management"
            status="online"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "99.9%" },
              { label: "Response Time", value: "45ms" },
              { label: "Active Users", value: "124" },
              { label: "Requests/min", value: "1.2k" },
            ]}
            delay={0.1}
          />
          <StatusCard
            title="Appointment Scheduling"
            status="online"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "99.8%" },
              { label: "Response Time", value: "52ms" },
              { label: "Active Users", value: "89" },
              { label: "Requests/min", value: "890" },
            ]}
            delay={0.2}
          />
          <StatusCard
            title="Billing & Invoicing"
            status="slow"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "98.5%" },
              { label: "Response Time", value: "180ms" },
              { label: "Active Users", value: "45" },
              { label: "Requests/min", value: "450" },
            ]}
            delay={0.3}
          />
          <StatusCard
            title="Electronic Health Records"
            status="online"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "99.7%" },
              { label: "Response Time", value: "68ms" },
              { label: "Active Users", value: "156" },
              { label: "Requests/min", value: "2.1k" },
            ]}
            delay={0.4}
          />
          <StatusCard
            title="Laboratory Integration"
            status="slow"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "97.2%" },
              { label: "Response Time", value: "220ms" },
              { label: "Active Users", value: "23" },
              { label: "Requests/min", value: "340" },
            ]}
            delay={0.5}
          />
          <StatusCard
            title="Pharmacy System"
            status="online"
            icon={Activity}
            metrics={[
              { label: "Uptime", value: "99.5%" },
              { label: "Response Time", value: "58ms" },
              { label: "Active Users", value: "67" },
              { label: "Requests/min", value: "780" },
            ]}
            delay={0.6}
          />
        </div>
      </div>
    </div>
  );
}
