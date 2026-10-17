const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 10000;
const DEMO_PASSWORD = process.env.DEMO_PASSWORD || 'PestoCliente26!';
const PANEL_PATH = process.env.PANEL_PATH || 'painel-acessos-7kq2m9';
const DEMO_ORIGIN = 'https://pesto-cozinha-bar.onrender.com';
const events = [];
app.disable('x-powered-by');
app.use(express.json({limit:'5kb'}));
app.use((req,res,next)=>{res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');next();});
app.use('/api',(req,res,next)=>{if(req.headers.origin===DEMO_ORIGIN){res.setHeader('Access-Control-Allow-Origin',DEMO_ORIGIN);res.setHeader('Vary','Origin');}res.setHeader('Access-Control-Allow-Methods','POST, GET, OPTIONS');res.setHeader('Access-Control-Allow-Headers','Content-Type');if(req.method==='OPTIONS')return res.sendStatus(204);next();});
function classify(ua=''){
 let browser='Não identificado';
 if(/Edg\//i.test(ua))browser='Microsoft Edge';else if(/SamsungBrowser/i.test(ua))browser='Samsung Internet';else if(/OPR\//i.test(ua))browser='Opera';else if(/Firefox\//i.test(ua))browser='Firefox';else if(/Chrome\//i.test(ua))browser='Chrome';else if(/Safari\//i.test(ua))browser='Safari';
 let os='Não identificado';if(/Android/i.test(ua))os='Android';else if(/iPhone|iPad|iPod/i.test(ua))os='iOS/iPadOS';else if(/Windows/i.test(ua))os='Windows';else if(/Mac OS X|Macintosh/i.test(ua))os='macOS';else if(/Linux/i.test(ua))os='Linux';
 let device='Computador';if(/iPad|Tablet/i.test(ua))device='Tablet';else if(/Mobile|Android|iPhone|iPod/i.test(ua))device='Celular';
 return {browser,os,device};
}
app.post('/api/login',(req,res)=>{
 if(String(req.body?.password||'')!==DEMO_PASSWORD)return res.status(401).json({ok:false});
 const details=classify(String(req.headers['user-agent']||'').slice(0,400));
 const event={id:Date.now().toString(36)+Math.random().toString(36).slice(2,6),timestamp:new Date().toISOString(),...details};
 events.unshift(event);if(events.length>500)events.length=500;
 console.log('DEMO_LOGIN '+JSON.stringify(event));
 res.json({ok:true});
});
app.get('/'+PANEL_PATH,(req,res)=>res.sendFile(path.join(__dirname,'index.html')));
app.get('/api/events',(req,res)=>{res.setHeader('Cache-Control','no-store');res.json({events,count:events.length,temporary:true});});
app.get('/health',(req,res)=>res.json({ok:true}));
app.listen(PORT,'0.0.0.0',()=>console.log('Audit service ready on '+PORT));