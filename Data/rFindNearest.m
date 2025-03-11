% find nearest number in vector vA to n
% made for finding a specific frequency in a scale
% or the index of a specific time stamp in a time vector
% vA = input 
% n = number
% RAFF 2/14/2007

function [index,num] = rFindNearest(vA,n);

vB = n*ones(size(vA));
[num,index] = min(abs(vA - vB));


%% old function
% vA = reshape(vA,[],1);
% vAux = n*ones(size(vA));
% vDiff = abs(vA - vAux);
% [num,index] = min(vDiff);
% index = index + 1;