import { Bell, AlertCircle, CheckCircle, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

const notifications = [
  {
    id: 1,
    type: "alert",
    icon: AlertCircle,
    title: "High system load detected",
    message: "Billing module experiencing increased response times",
    time: "2 minutes ago",
    unread: true,
  },
  {
    id: 2,
    type: "success",
    icon: CheckCircle,
    title: "Backup completed successfully",
    message: "Daily backup of patient records completed",
    time: "1 hour ago",
    unread: true,
  },
  {
    id: 3,
    type: "info",
    icon: Info,
    title: "System maintenance scheduled",
    message: "Scheduled maintenance on Sunday 2:00 AM - 4:00 AM",
    time: "3 hours ago",
    unread: false,
  },
];

export default function Notifications() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications Center</h1>
          <p className="text-muted-foreground">Stay updated with system alerts and messages</p>
        </div>
        <Button className="bg-gradient-primary shadow-glow">
          <Bell className="mr-2 h-4 w-4" />
          Create Alert
        </Button>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-4">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4 mt-6">
          {notifications.map((notification, index) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className={notification.unread ? "border-primary/50" : ""}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-full ${
                        notification.type === "alert"
                          ? "bg-destructive/10"
                          : notification.type === "success"
                          ? "bg-success/10"
                          : "bg-primary/10"
                      }`}
                    >
                      <notification.icon
                        className={`h-5 w-5 ${
                          notification.type === "alert"
                            ? "text-destructive"
                            : notification.type === "success"
                            ? "text-success"
                            : "text-primary"
                        }`}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold mb-1">{notification.title}</h3>
                          <p className="text-sm text-muted-foreground mb-2">{notification.message}</p>
                          <p className="text-xs text-muted-foreground">{notification.time}</p>
                        </div>
                        {notification.unread && (
                          <div className="h-2 w-2 rounded-full bg-primary animate-pulse-glow" />
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>System Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">No new alerts</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>System Notifications</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">No system notifications</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="messages" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Messages</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">No new messages</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
