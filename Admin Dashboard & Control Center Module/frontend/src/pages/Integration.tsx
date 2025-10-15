import { Layers, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";

const integrations = [
  {
    id: 1,
    name: "Patient Management API",
    status: "connected",
    lastSync: "5 minutes ago",
    requests: "1,234",
  },
  {
    id: 2,
    name: "Laboratory System",
    status: "connected",
    lastSync: "12 minutes ago",
    requests: "567",
  },
  {
    id: 3,
    name: "Pharmacy Integration",
    status: "disconnected",
    lastSync: "2 hours ago",
    requests: "0",
  },
  {
    id: 4,
    name: "Insurance Provider API",
    status: "connected",
    lastSync: "8 minutes ago",
    requests: "892",
  },
];

export default function Integration() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Integration Panel</h1>
          <p className="text-muted-foreground">Manage external system connections and data sync</p>
        </div>
        <Button className="bg-gradient-primary shadow-glow">
          <RefreshCw className="mr-2 h-4 w-4" />
          Sync All
        </Button>
      </div>

      {/* Sync Status */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle>Data Synchronization</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Overall Progress</span>
                <span className="text-sm text-muted-foreground">75%</span>
              </div>
              <Progress value={75} className="h-2" />
            </div>
            <div className="grid grid-cols-3 gap-4 pt-4 border-t">
              <div>
                <p className="text-sm text-muted-foreground">Records Synced</p>
                <p className="text-2xl font-bold">2,847</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pending</p>
                <p className="text-2xl font-bold">412</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Failed</p>
                <p className="text-2xl font-bold text-destructive">23</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Integration Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        {integrations.map((integration, index) => (
          <motion.div
            key={integration.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Layers className="h-5 w-5 text-primary" />
                    {integration.name}
                  </CardTitle>
                  {integration.status === "connected" ? (
                    <CheckCircle className="h-5 w-5 text-success" />
                  ) : (
                    <XCircle className="h-5 w-5 text-destructive" />
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Status</p>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        integration.status === "connected"
                          ? "bg-success/10 text-success"
                          : "bg-destructive/10 text-destructive"
                      }`}
                    >
                      {integration.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Requests</p>
                    <p className="font-semibold">{integration.requests}</p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Last Sync</p>
                  <p className="text-sm">{integration.lastSync}</p>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    Test Connection
                  </Button>
                  <Button size="sm" className="flex-1 bg-gradient-primary">
                    <RefreshCw className="mr-1 h-3 w-3" />
                    Sync
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
