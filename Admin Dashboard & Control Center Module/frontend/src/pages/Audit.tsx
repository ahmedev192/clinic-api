import { FileCheck, Download, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { motion } from "framer-motion";

const auditLogs = [
  {
    id: 1,
    user: "admin@clinicos.com",
    action: "Created Patient Record",
    module: "Patients",
    timestamp: "2025-10-11 14:32:15",
    ip: "192.168.1.100",
  },
  {
    id: 2,
    user: "doctor@clinicos.com",
    action: "Updated Appointment",
    module: "Appointments",
    timestamp: "2025-10-11 14:28:42",
    ip: "192.168.1.105",
  },
  {
    id: 3,
    user: "accountant@clinicos.com",
    action: "Generated Invoice",
    module: "Billing",
    timestamp: "2025-10-11 14:15:33",
    ip: "192.168.1.112",
  },
  {
    id: 4,
    user: "admin@clinicos.com",
    action: "Modified User Role",
    module: "Settings",
    timestamp: "2025-10-11 13:58:21",
    ip: "192.168.1.100",
  },
];

export default function Audit() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit & Compliance</h1>
          <p className="text-muted-foreground">Track system activities and generate compliance reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Filter
          </Button>
          <Button className="bg-gradient-primary shadow-glow">
            <Download className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Compliance Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        {[
          { title: "Total Logs", value: "12,847", color: "primary" },
          { title: "Compliance Score", value: "98.5%", color: "success" },
          { title: "Critical Events", value: "3", color: "warning" },
        ].map((item, index) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className={`border-${item.color}/20 bg-${item.color}/5`}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold text-${item.color}`}>{item.value}</div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Audit Logs Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileCheck className="h-5 w-5" />
              Recent Audit Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Module</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>IP Address</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="font-medium">{log.user}</TableCell>
                    <TableCell>{log.action}</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                        {log.module}
                      </span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{log.timestamp}</TableCell>
                    <TableCell className="text-muted-foreground">{log.ip}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
