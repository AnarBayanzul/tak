// npx vite
// in terminal to start hosting server

"use strict";
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const canvas = document.querySelector('#c');
const scene = new THREE.Scene(); {
    const color = 0xFFFFFF;
    const intensity = 3;
    const directionalLight = new THREE.DirectionalLight(color, intensity);
    directionalLight.position.set(-1, 2, 4);
    directionalLight.castShadow = true;
    directionalLight.shadowMapWidth = 2048
    directionalLight.shadowMapHeight = 2048
    const ambientLight = new THREE.AmbientLight(0xC1D1DB);
    scene.add(directionalLight);
    scene.add(ambientLight);
}
scene.background = new THREE.Color(0xC1D1DB);
// FOV, Aspect ratio, near, far
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.01, 5);

const renderer = new THREE.WebGLRenderer({antialias: true, canvas});
renderer.setSize( window.innerWidth, window.innerHeight, false );
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;


document.body.appendChild( renderer.domElement );

// Orbit Controls
const controls = new OrbitControls(camera, renderer.domElement);
// Don't go below the ground
controls.maxPolarAngle = Math.PI / 2 - 0.01;
// Zoom limitations
controls.minDistance = 0.3;
controls.maxDistance = 4;
controls.enableDamping = true;
controls.dampingFactor = 0.1;
camera.position.z = 1;
camera.position.y = 1;
controls.update();
















// # of stones and capstones for each player based on boardSize
// Two or less doesn't exist (just for testing)
//                      0,  1,  2,  3,  4,  5,  6,  7,  8
const stoneCounts    = [0,  0,  2, 10, 15, 21, 30, 40, 50];
const capstoneCounts = [0,  0,  0,  0,  0,  1,  1,  2,  2];

const boardSize = 4;
const whiteColor = 0xe5cbc2;
const blackColor = 0x7e4735;
const whiteStones = stoneCounts[boardSize];
const whiteCaps = capstoneCounts[boardSize];
const blackStones = stoneCounts[boardSize];
const blackCaps = capstoneCounts[boardSize];







// TODO: FIND A WAY TO GET BOARD FROM TAK.PY
let boardState = [];
let pillar = [];
let column = [];
for (let i = 0; i < boardSize; i++) {
    column = []
    for (let j = 0; j < boardSize; j++) {
        pillar = []
        for (let k = 0; k < (2 * stoneCounts[boardSize] + capstoneCounts[boardSize]); k++) {
            pillar.push("  ")
        }
        column.push(pillar);
    }
    boardState.push(column);
}




























const boardWidth = 1;
const boardHeight = 0.1;
const boardDepth = 1;

const pieceDimension = 1 / boardSize;

const whiteMat = new THREE.MeshPhongMaterial({color: whiteColor});
const blackMat = new THREE.MeshPhongMaterial({color: blackColor});

const roadGeo = new THREE.BoxGeometry(pieceDimension / 1.5, pieceDimension / 4, pieceDimension / 1.5);
const capGeo = new THREE.ConeGeometry(pieceDimension / 2, pieceDimension, 6);

const whitePiece = new THREE.InstancedMesh(roadGeo, whiteMat, stoneCounts[boardSize]);
const blackPiece = new THREE.InstancedMesh(roadGeo, blackMat, stoneCounts[boardSize]);
const whiteCap = new THREE.InstancedMesh(capGeo, whiteMat, capstoneCounts[boardSize]);
const blackCap = new THREE.InstancedMesh(capGeo, blackMat, capstoneCounts[boardSize]);


whitePiece.position.y = pieceDimension / 8;
blackPiece.position.y = pieceDimension / 8;
whiteCap.position.y = pieceDimension / 2;
blackCap.position.y = pieceDimension / 2;

whitePiece.castShadow = true;
whitePiece.receiveShadow = true;
blackPiece.castShadow = true;
blackPiece.receiveShadow = true;
whiteCap.castShadow = true;
whiteCap.receiveShadow = true;
blackCap.castShadow = true;
blackCap.receiveShadow = true;


scene.add(whitePiece);
scene.add(blackPiece);
scene.add(whiteCap);
scene.add(blackCap);









// x, z, y
boardState[1][2][0] = 'wF';
boardState[1][3][0] = "bF";
boardState[1][3][1] = 'wF';
boardState[1][3][2] = 'wF';
boardState[2][0][0] = "bF";
boardState[3][3][0] = "bF";
boardState[0][0][4] = "wF";

console.log(boardState);


// let translationMatrix;
// translationMatrix = new THREE.Matrix4().makeTranslation(0.3, 0, 0.3);
// whitePiece.setMatrixAt(0, translationMatrix)









// Place 
function showBoard(boardState) {
    let piece;
    let xPos, zPos, yPos;
    let translationMatrix;
    let whitePieceIndex = 0;
    let blackPieceIndex = 0;
    let whiteCapIndex = 0;
    let blackCapIndex = 0;
    // Put pieces on board
    for (let x = 0; x < boardSize; x++) {
        for (let z = 0; z < boardSize; z++) {
            for (let y = 0; y < (2 * stoneCounts[boardSize] + capstoneCounts[boardSize]); y++) {
                piece = boardState[x][z][y];
                xPos = -boardWidth / 2 + pieceDimension / 2 + pieceDimension * x;
                yPos = y * pieceDimension / 4; 
                zPos =  boardWidth / 2 - pieceDimension / 2 - pieceDimension * z;
                translationMatrix = new THREE.Matrix4().makeTranslation(xPos, yPos, zPos);
                
                switch(piece) {
                    case "wF":
                        whitePiece.setMatrixAt(whitePieceIndex, translationMatrix);
                        whitePieceIndex++;
                        break;
                    case "wS":
                        whitePiece.setMatrixAt(whitePieceIndex, translationMatrix);
                        // Add rotation for wall
                        whitePieceIndex++;
                        break;
                    case "wC":
                        whiteCap.setMatrixAt(whiteCapIndex, translationMatrix);
                        whiteCapIndex++;
                        break;
                    case "bF":
                        blackPiece.setMatrixAt(blackPieceIndex, translationMatrix);
                        blackPieceIndex++;
                        break;
                    case "bS":
                        blackPiece.setMatrixAt(blackPieceIndex, translationMatrix);
                        // Add rotation for wall
                        blacPieceIndex++;
                        break;
                    case "bC":
                        blackCap.setMatrixAt(blackCapIndex, translationMatrix);
                        blackCapIndex++;
                        break;
                    default:
                        break;
                }
            }
        }
    }

    // Put remaining pieces on table
    for (let i = whitePieceIndex; i < stoneCounts[boardSize]; i++) {
        translationMatrix = new THREE.Matrix4().makeTranslation(-pieceDimension / 2, -3 * pieceDimension / 8, 3 / 4);
        whitePiece.setMatrixAt(i, translationMatrix);
    }
    for (let i = whiteCapIndex; i < capstoneCounts[boardSize]; i++) {
        translationMatrix = new THREE.Matrix4().makeTranslation(pieceDimension / 2, -3 * pieceDimension / 8, 3 / 4);
        whiteCap.setMatrixAt(i, translationMatrix);
    }
    for (let i = blackPieceIndex; i < stoneCounts[boardSize]; i++) {
        translationMatrix = new THREE.Matrix4().makeTranslation(pieceDimension / 2, -3 * pieceDimension / 8, -3 / 4);
        blackPiece.setMatrixAt(i, translationMatrix);
    }
    for (let i = blackCapIndex; i < capstoneCounts[boardSize]; i++) {
        translationMatrix = new THREE.Matrix4().makeTranslation(-pieceDimension / 2, -3 * pieceDimension / 8, -3 / 4);
        blackCap.setMatrixAt(i, translationMatrix);
    }
}







// Load board texture
const boardTexture = new THREE.TextureLoader().load("textures/board.jpg");
boardTexture.wrapS = THREE.RepeatWrapping;
boardTexture.wrapT = THREE.RepeatWrapping;
boardTexture.repeat.set(boardSize / 2, boardSize / 2);
// Board Geometry
const boardGeo = new THREE.BoxGeometry(boardWidth, boardHeight, boardDepth);

const blankMat = new THREE.MeshPhongMaterial({color: 0x6A4940});
const boardMat = new THREE.MeshPhongMaterial({map:boardTexture});
const board = new THREE.Mesh(boardGeo, [
        blankMat,
        blankMat,
        boardMat,
        blankMat,
        blankMat,
        blankMat
    ]
);
scene.add(board);
board.position.set(0, -boardHeight / 2, 0);
board.castShadow = false;
board.receiveShadow = true;
//Board Border
const borderGeo = new THREE.BoxGeometry(boardWidth * 1.3, boardHeight / 2, boardDepth * 1.3);
const border = new THREE.Mesh(borderGeo, blankMat);
scene.add(border);
border.position.set(0, -3 * boardHeight / 4, 0);
border.castShadow = true;
border.receiveShadow = true;
// Table
const tableMat = new THREE.MeshPhongMaterial({color: 0xEED5AE});
const tableGeo = new THREE.BoxGeometry(boardWidth * 2, boardHeight / 2, boardDepth * 2);
const table = new THREE.Mesh(tableGeo, tableMat);
scene.add(table);
table.position.set(0, -boardHeight, 0);
table.castShadow = true;
table.receiveShadow = false;

function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    const width = canvas. clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
        renderer.setSize(width, height, false);
    }
    return needResize;
}

function animate() {


    if (resizeRendererToDisplaySize){
        const canvas = renderer.domElement;
        camera.aspect = canvas.clientWidth / canvas.clientHeight;
        camera.updateProjectionMatrix();
    }

    // Display board
    showBoard(boardState);



    controls.update();
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
}
animate();