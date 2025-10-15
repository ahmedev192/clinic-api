import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface StatusCardProps {
  title: string;
  status: "online" | "slow" | "offline";
  icon: LucideIcon;
  metrics?: {
    label: string;
    value: string;
  }[];
  delay?: number;
}

export function StatusCard({ title, status, icon: Icon, metrics, delay = 0 }: StatusCardProps) {
  const statusConfig = {
    online: {
      color: "success",
      bgColor: "bg-success/10",
      borderColor: "border-success/20",
      label: "Operational",
    },
    slow: {
      color: "warning",
      bgColor: "bg-warning/10",
      borderColor: "border-warning/20",
      label: "Degraded",
    },
    offline: {
      color: "destructive",
      bgColor: "bg-destructive/10",
      borderColor: "border-destructive/20",
      label: "Offline",
    },
  };

  const config = statusConfig[status];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3 }}
    >
      <Card className={cn("border-2 transition-all hover:shadow-medium", config.borderColor)}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Icon className="h-5 w-5 text-primary" />
              {title}
            </CardTitle>
            <div className="flex items-center gap-2">
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className={cn("h-3 w-3 rounded-full", `bg-${config.color}`)}
              />
              <span className={cn("text-sm font-medium", `text-${config.color}`)}>
                {config.label}
              </span>
            </div>
          </div>
        </CardHeader>
        {metrics && (
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {metrics.map((metric, index) => (
                <div key={index} className={cn("rounded-lg p-3", config.bgColor)}>
                  <p className="text-xs text-muted-foreground mb-1">{metric.label}</p>
                  <p className="text-lg font-semibold">{metric.value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
}
