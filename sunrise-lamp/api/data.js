// api/data.js
export default function handler(req, res) {
  res.status(200).json({
    name: 'Vihas',
    project: 'MotionMinder',
    status: 'In progress'
  });
}
