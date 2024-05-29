%% CREATE ANSYS DISPLACEMENT BC FILES
% Author: Lloyd Fletcher
% Image-Based Mechanics Group (IBMG), University of Southampton
% Date Created: 1/5/2020
% Date Edited: 1/5/2020

clc
clear variables
close all

savePath = pwd;

% Specimen height in mm
specEdgeL = 40e-3;

specElemSize = 1e-3;
specElemQuad = true;
if specElemQuad
    specNodeStep = specElemSize/2;
else
    specNodeStep = specElemSize;
end

% Nodal locations - doesn't matter if this isn't correct because ANSYS
% table variable will linearly interpolate
specEdgeLoc = 0:specNodeStep:specEdgeL;

% Options for creating ux displacement
uxDispType = 'quadratic'; % 'fixed', 'linear' or 'quadratic'
uxRelPeak = 0.3e-3;     % Peak displacement (doesn't include offset) 
uxOffset = 0.3e-3;      % Fixed displacement offset added to all nodes

% Options for creating uy displacement
uyDispType = 'fixed';
uyRelPeak = 0.0e-3;
uyOffset = 0.0e-3; 

uxVec = zeros(length(specEdgeLoc),1); 
uyVec = zeros(length(specEdgeLoc),1); 
for pp = 1:length(specEdgeLoc)
    if strcmp(uxDispType,'quadratic')
        uxVec(pp) = specEdgeLoc(pp)*(specEdgeL - specEdgeLoc(pp))*...
            uxRelPeak/(specEdgeL/2)^2 + uxOffset;
    elseif strcmp(uxDispType,'linear')
        uxVec(pp) = uxRelPeak/specEdgeL*specEdgeLoc(pp) + uxOffset;
    end
    if strcmp(uyDispType,'quadratic')
        uyVec(pp) = specEdgeLoc(pp)*(specEdgeL - specEdgeLoc(pp))*...
            uyRelPeak/(specEdgeL/2)^2 + uyOffset;
    elseif strcmp(uyDispType,'linear')
        uyVec(pp) = uyRelPeak/specEdgeL*specEdgeLoc(pp) + uyOffset;
    end
end 

edgeBCsX = [specEdgeLoc',uxVec];
edgeBCsY = [specEdgeLoc',uyVec];
csvwrite('edgeBCDx.csv',edgeBCsX);
csvwrite('edgeBCDy.csv',edgeBCsY);

% Plot the expected displacement for debugging
figure;
subplot(1,2,1)
plot(specEdgeLoc,uxVec,'-+')
xlabel('Pos. [m]')
ylabel('Disp. BC X [m]')
box on
grid on

subplot(1,2,2)
plot(specEdgeLoc,uyVec,'-+')
xlabel('Pos. [m]')
ylabel('Disp. BC Y [m]')
box on
grid on


