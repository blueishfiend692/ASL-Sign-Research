import torch
import torch.nn as nn
import torch.nn.functional as F

from Lit import LitModel # Class containing all Lightning functions

class Encoder(LitModel):
  """
  Class for Encoder Model, subclass of Lightning Module

  Implements a classification token, postional embedding, encoder table and linear output for classification
  """
  def __init__(self,learning_rate,
               layers=1,
               number_heads = 1,
               input_size=5,
               hidden_size=32,
               classes=36,
               time_steps=10,
               dropout=0.2):
    super().__init__()
    # set hyperparamters
    self.lr = learning_rate # used in optimizers for lightning module
    self.dim = input_size
    self.classes = classes


    self.classification_embedding = nn.Embedding(1,hidden_size) # CLS token
    self.embedding_table = nn.Linear(input_size,hidden_size) # input embedding table
    self.time_steps = time_steps + 1 # add one for postional embedding
    self.pos_embedding_table = nn.Embedding(self.time_steps, hidden_size) # positional embedding vectors
    encoder_layer = nn.TransformerEncoderLayer(hidden_size,
                                                number_heads,
                                                dim_feedforward=4*hidden_size,
                                                activation='relu',
                                                norm_first=True,
                                                batch_first=True)
    self.transformerEncoder = nn.TransformerEncoder(encoder_layer,layers, enable_nested_tensor=False)
    self.linear_output = nn.Linear(hidden_size, classes)

  def forward(self, x_input, y_targets):
    classification_embedding = self.classification_embedding(torch.zeros((x_input.shape[0]),dtype=int).to(self.device))
    classification_embedding = torch.unsqueeze(classification_embedding,dim=1)
    x_input = self.embedding_table(x_input)
    x_input = torch.cat((classification_embedding, x_input), dim=1) # (32 x 1 x hidden_size) + (32 x T x hidden+size)
    pos = self.pos_embedding_table(torch.arange(self.time_steps).to(self.device))
    x = x_input + pos # add positional embedding to vector embeddings
    x = self.transformerEncoder(x)
    x = x[:,0,:]
    logits = self.linear_output(x)
    loss = F.cross_entropy(logits, y_targets)
    return logits, loss
