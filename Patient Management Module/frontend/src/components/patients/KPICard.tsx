import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    positive: boolean;
  };
  delay?: number;
}

export const KPICard = ({ title, value, icon: Icon, trend, delay = 0 }: KPICardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ y: -4, boxShadow: 'var(--shadow-medium)' }}
    >
      <Card className="relative overflow-hidden bg-gradient-card border-border/50 hover:border-primary/20 transition-all shadow-soft">
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-primary opacity-10 rounded-full -mr-16 -mt-16" />
        
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground mb-2">
                {title}
              </p>
              <h3 className="text-3xl font-bold text-foreground mb-2 animate-counter-up">
                {value}
              </h3>
              
              {trend && (
                <div className={`text-xs font-medium ${trend.positive ? 'text-success' : 'text-destructive'}`}>
                  {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}% from last month
                </div>
              )}
            </div>
            
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
              <Icon className="h-6 w-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
