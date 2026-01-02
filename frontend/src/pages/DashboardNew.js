import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Users, Target, Building2, FileText, Calendar, AlertCircle, Clock, ChevronRight } from 'lucide-react';

const Dashboard = () => {
  const [kpiData, setKpiData] = useState({
    leads: { total: 50, active: 20, delayed: 5, rejected: 10 },
    opportunities: { total: 30, active: 12, delayed: 3, rejected: 6 },
    projects: { total: 10, active: 6, delayed: 2, rejected: 1 },
    sows: { total: 8, active: 5, delayed: 1, rejected: 0 }
  });
  
  const [showKpiPopup, setShowKpiPopup] = useState(false);
  const [selectedKpi, setSelectedKpi] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sample task tracker data
  const [tasks] = useState([
    {
      module: 'Leads',
      itemName: 'L-001',
      taskName: 'Follow up with client',
      assignee: 'John Doe',
      status: 'Active',
      priority: 'High',
      dueDate: '2024-01-20',
      pendingLevel: 'L1'
    },
    {
      module: 'Opportunities',
      itemName: 'O-003',
      taskName: 'Prepare proposal',
      assignee: 'Jane Smith',
      status: 'Delayed',
      priority: 'Critical',
      dueDate: '2024-01-15',
      pendingLevel: 'L2'
    },
    {
      module: 'Projects',
      itemName: 'P-002',
      taskName: 'Review deliverables',
      assignee: 'Mike Johnson',
      status: 'Active',
      priority: 'Medium',
      dueDate: '2024-01-25',
      pendingLevel: 'L1'
    },
    {
      module: 'SOW',
      itemName: 'SOW-004',
      taskName: 'Finalize terms',
      assignee: 'Sarah Wilson',
      status: 'Pending',
      priority: 'High',
      dueDate: '2024-01-22',
      pendingLevel: 'L3'
    }
  ]);

  // Sample assignee breakdown data
  const [assigneeData] = useState([
    { name: 'John Doe', pending: 3, active: 5, delayed: 1 },
    { name: 'Jane Smith', pending: 2, active: 4, delayed: 2 },
    { name: 'Mike Johnson', pending: 1, active: 6, delayed: 0 },
    { name: 'Sarah Wilson', pending: 4, active: 2, delayed: 1 }
  ]);

  const handleKpiClick = (module, metric) => {
    setSelectedKpi({ module, metric });
    setShowKpiPopup(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      'Active': 'bg-blue-100 text-blue-800',
      'Delayed': 'bg-red-100 text-red-800',
      'Pending': 'bg-yellow-100 text-yellow-800',
      'Completed': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'Critical': 'bg-red-600 text-white',
      'High': 'bg-red-100 text-red-800',
      'Medium': 'bg-orange-100 text-orange-800',
      'Low': 'bg-gray-100 text-gray-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  const getPendingLevelColor = (level) => {
    const colors = {
      'L1': 'bg-green-100 text-green-800',
      'L2': 'bg-yellow-100 text-yellow-800',
      'L3': 'bg-red-100 text-red-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const moduleIcons = {
    leads: Users,
    opportunities: Target,
    projects: Building2,
    sows: FileText
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-600">Role-aware operational overview</p>
      </div>

      {/* KPI Cards Section */}
      <div className="space-y-4">
        {Object.entries(kpiData).map(([module, data]) => {
          const Icon = moduleIcons[module];
          return (
            <div key={module} className="flex items-center gap-2">
              <Icon className="h-4 w-4 text-slate-500" />
              <span className="text-sm font-medium text-slate-700 capitalize w-20">{module}</span>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleKpiClick(module, 'total')}
                  className="h-6 px-2 text-xs bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100"
                >
                  Total {data.total}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleKpiClick(module, 'active')}
                  className="h-6 px-2 text-xs bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
                >
                  Active {data.active}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleKpiClick(module, 'delayed')}
                  className="h-6 px-2 text-xs bg-red-50 text-red-700 border-red-200 hover:bg-red-100"
                >
                  Delayed {data.delayed}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleKpiClick(module, 'rejected')}
                  className="h-6 px-2 text-xs bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                >
                  Rejected {data.rejected}
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Task Tracker Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Task Tracker
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-xs">Module</TableHead>
                <TableHead className="text-xs">Item ID</TableHead>
                <TableHead className="text-xs">Task</TableHead>
                <TableHead className="text-xs">Assignee</TableHead>
                <TableHead className="text-xs">Status</TableHead>
                <TableHead className="text-xs">Priority</TableHead>
                <TableHead className="text-xs">Due Date</TableHead>
                <TableHead className="text-xs">Pending Level</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tasks.map((task, index) => (
                <TableRow key={index} className={task.status === 'Delayed' ? 'bg-red-50' : ''}>
                  <TableCell className="text-xs font-medium capitalize">{task.module}</TableCell>
                  <TableCell className="text-xs">{task.itemName}</TableCell>
                  <TableCell className="text-xs">{task.taskName}</TableCell>
                  <TableCell className="text-xs">{task.assignee}</TableCell>
                  <TableCell className="text-xs">
                    <Badge className={getStatusColor(task.status)}>
                      {task.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    <Badge className={getPriorityColor(task.priority)}>
                      {task.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs">{task.dueDate}</TableCell>
                  <TableCell className="text-xs">
                    <Badge className={getPendingLevelColor(task.pendingLevel)}>
                      {task.pendingLevel}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* KPI Popup Dialog */}
      <Dialog open={showKpiPopup} onOpenChange={setShowKpiPopup}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedKpi && moduleIcons[selectedKpi.module] && (
                React.createElement(moduleIcons[selectedKpi.module], { className: "h-5 w-5" })
              )}
              {selectedKpi && `${selectedKpi.module.toUpperCase()} - ${selectedKpi.metric.toUpperCase()} Breakdown`}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <p className="text-sm text-slate-600">Assignee-wise breakdown</p>
            {assigneeData.map((assignee, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium text-sm">{assignee.name}</p>
                  <div className="flex gap-2 mt-1">
                    <span className="text-xs text-slate-500">Pending: {assignee.pending}</span>
                    <span className="text-xs text-slate-500">Active: {assignee.active}</span>
                    <span className="text-xs text-red-500">Delayed: {assignee.delayed}</span>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 text-slate-400" />
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;
