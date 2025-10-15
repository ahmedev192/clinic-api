import { UserPlus, UserCog, FileText, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

const actions = [
  { icon: UserCog, label: "Add Doctor", color: "bg-primary" },
  { icon: UserPlus, label: "Add Patient", color: "bg-accent" },
  { icon: FileText, label: "View Reports", color: "bg-success" },
  { icon: RefreshCw, label: "Sync Data", color: "bg-warning" },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {actions.map((action, index) => (
            <motion.div
              key={action.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                variant="outline"
                className="h-auto flex-col gap-3 p-6 w-full border-2 hover:border-primary/50 hover:shadow-medium transition-all"
              >
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${action.color} shadow-glow`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <span className="text-sm font-medium">{action.label}</span>
              </Button>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
